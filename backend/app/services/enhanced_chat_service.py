"""
Enhanced Chat Service for Fortes Education
Integrates guardrails, attribution, observability, and advanced RAG features
"""

import json
import base64
import logging
from typing import List, AsyncGenerator, Dict, Any, Optional
from sqlalchemy.orm import Session
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from app.core.config import settings
from app.models.chat import Message
from app.models.knowledge import KnowledgeBase, Document
from app.services.vector_store import VectorStoreFactory
from app.services.embedding.embedding_factory import EmbeddingsFactory
from app.services.llm.llm_factory import LLMFactory
from app.services.guardrails import guardrails_service
from app.services.attribution import attribution_service
from app.services.observability import observability_service

logger = logging.getLogger(__name__)


async def generate_enhanced_response(
    query: str,
    messages: dict,
    knowledge_base_ids: List[int],
    chat_id: int,
    db: Session
) -> AsyncGenerator[str, None]:
    """
    Enhanced response generation with guardrails, attribution, and observability
    """
    try:
        # Step 1: Apply input guardrails
        guardrail_result = guardrails_service.process_query(query)
        
        if guardrail_result["injection_detected"]:
            # Return refusal for severe injection attempts
            refusal = guardrails_service.create_refusal_response("injection")
            yield f'0:"{refusal}"\n'
            yield 'd:{"finishReason":"stop","usage":{"promptTokens":0,"completionTokens":0}}\n'
            
            # Log the incident
            logger.warning(f"Blocked injection attempt: {guardrail_result['injection_reason']}")
            return
        
        # Use processed (PII-redacted, neutralized) query
        processed_query = guardrail_result["processed_query"]
        
        # Step 2: Check prompt cache
        corpus_id = "_".join(map(str, knowledge_base_ids))
        cached_response = observability_service.get_cached_response(query, corpus_id)
        
        if cached_response:
            logger.info("✓ Returning cached response")
            yield f'0:"{cached_response["response"]}"\n'
            yield f'd:{json.dumps(cached_response["metadata"])}\n'
            return
        
        # Create user message
        user_message = Message(
            content=query,
            role="user",
            chat_id=chat_id
        )
        db.add(user_message)
        db.commit()
        
        # Create bot message placeholder
        bot_message = Message(
            content="",
            role="assistant",
            chat_id=chat_id
        )
        db.add(bot_message)
        db.commit()
        
        # Step 3: Retrieve knowledge bases
        knowledge_bases = (
            db.query(KnowledgeBase)
            .filter(KnowledgeBase.id.in_(knowledge_base_ids))
            .all()
        )
        
        # Initialize embeddings
        embeddings = EmbeddingsFactory.create()
        
        # Log embedding model usage
        observability_service.log_embedding_request(
            text=processed_query,
            model=settings.EMBEDDING_MODEL
        )
        
        # Create vector stores
        vector_stores = []
        for kb in knowledge_bases:
            documents = db.query(Document).filter(Document.knowledge_base_id == kb.id).all()
            if documents:
                vector_store = VectorStoreFactory.create(
                    store_type=settings.VECTOR_STORE_TYPE,
                    collection_name=f"kb_{kb.id}",
                    embedding_function=embeddings,
                )
                vector_stores.append(vector_store)
        
        if not vector_stores:
            error_msg = "I don't have any knowledge base to help answer your question."
            yield f'0:"{error_msg}"\n'
            yield 'd:{"finishReason":"stop","usage":{"promptTokens":0,"completionTokens":0}}\n'
            bot_message.content = error_msg
            db.commit()
            return
        
        # Use first vector store
        retriever = vector_stores[0].as_retriever(
            search_kwargs={"k": settings.TOP_K_RETRIEVAL}
        )
        
        # Initialize LLM
        llm = LLMFactory.create()
        
        # Create contextualize question prompt
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, just "
            "reformulate it if needed and otherwise return it as is."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])
        
        # Create history aware retriever
        history_aware_retriever = create_history_aware_retriever(
            llm, 
            retriever,
            contextualize_q_prompt
        )

        # Enhanced QA prompt with Fortes Education branding
        qa_system_prompt = (
            "You are Fortes Education Assistant, an expert Q&A system powered by RAG technology. "
            "You will be given a user question and a set of related contexts to answer it. "
            "Each context has an implicit reference number based on its position (first context is 1, second is 2, etc.). "
            "Please provide a clean, concise, and accurate answer using these contexts. "
            "IMPORTANT: Cite your sources using the format [citation:x] at the end of each sentence where applicable. "
            "If a sentence draws from multiple contexts, list all citations, like [citation:1][citation:2]. "
            "If the contexts don't provide sufficient information, say 'I don't have enough information about' followed by the topic. "
            "Limit your answer to 1024 tokens. Be professional, unbiased, and concise.\n\n"
            "Context: {context}\n\n"
        )
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])

        document_prompt = PromptTemplate.from_template("\n\n- {page_content}\n\n")

        # Create QA chain
        question_answer_chain = create_stuff_documents_chain(
            llm,
            qa_prompt,
            document_variable_name="context",
            document_prompt=document_prompt
        )

        # Create retrieval chain
        rag_chain = create_retrieval_chain(
            history_aware_retriever,
            question_answer_chain,
        )

        # Prepare chat history
        chat_history = []
        for message in messages["messages"]:
            if message["role"] == "user":
                chat_history.append(HumanMessage(content=message["content"]))
            elif message["role"] == "assistant":
                if "__LLM_RESPONSE__" in message["content"]:
                    message["content"] = message["content"].split("__LLM_RESPONSE__")[-1]
                chat_history.append(AIMessage(content=message["content"]))

        # Step 4: Generate response and collect context
        full_response = ""
        retrieved_chunks = []
        context_sent = False
        
        async for chunk in rag_chain.astream({
            "input": processed_query,
            "chat_history": chat_history
        }):
            if "context" in chunk and not context_sent:
                # Extract and store chunks for attribution
                for idx, context in enumerate(chunk["context"]):
                    chunk_data = {
                        "doc_id": context.metadata.get("source", f"doc_{idx}"),
                        "chunk_id": f"chunk_{idx}",
                        "content": context.page_content,
                        "line_start": context.metadata.get("line_start", 0),
                        "line_end": context.metadata.get("line_end", 0),
                        "score": context.metadata.get("score", 0.8),  # Default score
                        "metadata": context.metadata
                    }
                    retrieved_chunks.append(chunk_data)
                
                # Calculate grounding score
                grounding_score = attribution_service.calculate_grounding_score(retrieved_chunks)
                
                # Step 5: Validate grounding score
                is_grounded, refusal_message = guardrails_service.validate_grounding_score(
                    grounding_score, 
                    retrieved_chunks
                )
                
                if not is_grounded:
                    # Return refusal for low grounding
                    yield f'0:"{refusal_message}"\n'
                    yield f'd:{{"finishReason":"stop","grounding_score":{grounding_score:.3f}}}\n'
                    bot_message.content = refusal_message
                    db.commit()
                    return
                
                # Serialize and send context
                serializable_context = []
                for context in chunk["context"]:
                    serializable_doc = {
                        "page_content": context.page_content.replace('"', '\\"'),
                        "metadata": context.metadata,
                    }
                    serializable_context.append(serializable_doc)
                
                escaped_context = json.dumps({
                    "context": serializable_context,
                    "grounding_score": round(grounding_score, 3)
                })

                base64_context = base64.b64encode(escaped_context.encode()).decode()
                separator = "__LLM_RESPONSE__"
                
                yield f'0:"{base64_context}{separator}"\n'
                full_response += base64_context + separator
                context_sent = True

            if "answer" in chunk:
                answer_chunk = chunk["answer"]
                full_response += answer_chunk
                escaped_chunk = (answer_chunk
                    .replace('"', '\\"')
                    .replace('\n', '\\n'))
                yield f'0:"{escaped_chunk}"\n'
        
        # Step 6: Apply output guardrails (PII redaction)
        output_result = guardrails_service.process_response(full_response)
        final_response = output_result["processed_response"]
        
        # Step 7: Perform sentence-level attribution
        answer_only = final_response.split("__LLM_RESPONSE__")[-1] if "__LLM_RESPONSE__" in final_response else final_response
        annotated_sentences, has_hallucination, attribution_stats = attribution_service.annotate_response(
            answer_only,
            retrieved_chunks
        )
        
        # Format attribution for response
        attribution_data = attribution_service.format_citations_for_response(annotated_sentences)
        
        # Step 8: Log generation metrics
        observability_service.log_generation_request(
            prompt=processed_query,
            response=answer_only,
            model=settings.GENERATION_MODEL,
            metadata={
                "grounding_score": grounding_score if 'grounding_score' in locals() else 0.0,
                "has_hallucination": has_hallucination,
                "attribution_stats": attribution_stats,
                "pii_redacted": output_result["pii_redacted"]
            }
        )
        
        # Send final metadata
        final_metadata = {
            "finishReason": "stop",
            "grounding_score": round(grounding_score if 'grounding_score' in locals() else 0.0, 3),
            "has_hallucination": has_hallucination,
            "attribution": attribution_data,
            "guardrails": {
                "pii_redacted": output_result["pii_redacted"],
                "input_warnings": guardrail_result.get("warnings", [])
            }
        }
        
        yield f'd:{json.dumps(final_metadata)}\n'
        
        # Update bot message
        bot_message.content = final_response
        db.commit()
        
        # Cache the response
        observability_service.cache_response(
            query,
            corpus_id,
            {
                "response": final_response,
                "metadata": final_metadata
            }
        )
            
    except Exception as e:
        error_message = f"Error generating response: {str(e)}"
        logger.error(error_message, exc_info=True)
        yield f'3:"{error_message}"\n'
        
        if 'bot_message' in locals():
            bot_message.content = error_message
            db.commit()
    finally:
        db.close()

