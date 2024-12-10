import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.pydantic_v1 import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

# Initialize TavilySearchResults
os.environ['TAVILY_API_KEY'] = os.getenv("TAVILY_API_KEY")
internet_search = TavilySearchResults()
internet_search.name = "internet_search"
internet_search.description = "Returns a list of relevant document snippets for a textual query retrieved from the internet."


# Configuración de la página
st.set_page_config(
    page_title="ChatySUDo",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        max-width: 80%;
    }
    .user-message {
        background-color: #e6f3ff;
        margin-left: auto;
    }
    .bot-message {
        background-color: #f0f2f6;
        margin-right: auto;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 Chat con Documentos SUD")
st.header("🌟 Ilumina el Mundo")
st.markdown("""
        Barrio Sucre te invita a ser parte de la iniciativa 'Ilumina el Mundo'.
        Siguiendo el ejemplo de Jesucristo, podemos compartir Su luz a través del servicio y de amor.
        Visita [IluminaElMundo.org](https://www.iluminaelmundo.org) para más recursos.
        """)

st.markdown("""
        ### ¡Bienvenido a ChatySUDo!
        Este es un espacio no oficial para consultar y aprender sobre documentos SUD.
        Puedes hacer preguntas sobre los documentos del manual azul y mantener una conversación conmigo.

     💡 Recuerda:  Para decisiones importantes, consulta siempre con tus líderes locales.
        """)


class TavilySearchInput(BaseModel):
    query: str = Field(description="Query to search the internet with")

internet_search.args_schema = TavilySearchInput

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = os.getenv("OPENAI_MODEL")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "cache" not in st.session_state:
    st.session_state.cache = {}

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Check if the response is already in the cache
        if prompt in st.session_state.cache:
            full_response = st.session_state.cache[prompt]
            combined_response = full_response  # Ensure combined_response is defined
        else:
            # Perform internet search using TavilySearchResults
            search_query = f"{prompt} site:churchofjesuschrist.org"
            search_results = internet_search.run(search_query)

            # Combine search results with OpenAI response
            combined_response = f"Search Results:\n{search_results}\n\nChatySudo is 📚"

            for response in client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                max_tokens=50,  # Adjust the number of tokens
                temperature=0.01,  #
                stream=True,
            ):
                full_response += response.choices[0].delta.content or ""
                message_placeholder.markdown(combined_response  + "▌")
            message_placeholder.markdown(combined_response )

            # Store the response in the cache
            st.session_state.cache[prompt] = combined_response

    st.session_state.messages.append({"role": "assistant", "content": combined_response })

# Sidebar
with st.sidebar:
    st.header("📖 Acerca de")
    st.markdown("""
        Este chat fue creado para ayudarte a encontrar respuestas
        en los documentos oficiales de la Iglesia de Jesucristo de los Santos de los Últimos Días.
        """)

    st.markdown("---")

    # Clear chat
    if st.button("🗑️ Limpiar Chat", help="Elimina el historial de la conversación"):
        st.session_state.messages = []
        rag.clear_chat_history()
        st.rerun()

    st.markdown("---")
    st.header("🌟 Ilumina el Mundo")
    st.markdown("""
        #### ¿Cómo puedes participar?
        * Sirve a tu prójimo siguiendo el ejemplo de Jesucristo
        * Invita a otros a conocer más sobre el evangelio
        * Participa en actividades de servicio en tu comunidad

        Visita [IluminaElMundo.org](https://www.iluminaelmundo.org) para más información y recursos.
        """)

    st.markdown("---")

    st.header("👨‍👩‍👧‍👦 FamilySearch")
    st.markdown("""
        ### Descubre Tu Historia Familiar

        FamilySearch es el recurso genealógico más grande del mundo, ¡y es completamente gratuito!

        #### Lo que puedes hacer:
        * Crear tu árbol genealógico
        * Buscar registros históricos
        * Preservar fotos y memorias familiares
        * Conectar con familiares
        * Encontrar antepasados para la obra del templo


        [Visita FamilySearch.org](https://www.familysearch.org/es/) para comenzar tu búsqueda familiar.
        """)

# Espacio para asegurar que el footer aparezca después del chat
st.markdown("<br><br>", unsafe_allow_html=True)
