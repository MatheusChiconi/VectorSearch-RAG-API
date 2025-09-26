// Aguarda o carregamento completo do DOM antes de executar o script
document.addEventListener("DOMContentLoaded", () => {
    
    // Seleciona os elementos principais da interface
    const chatBox = document.querySelector(".overflow-y-auto");
    const inputField = document.querySelector(".custom-input");
    const initialMessage = document.querySelector(".flex.justify-center.items-center.h-full");

    // Função para obter o CSRF token dos cookies (essencial para a segurança do Django)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // Função para rolar o chat para a mensagem mais recente
    function scrollToBottom() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Função para exibir a mensagem do usuário na tela
    function displayUserMessage(message) {
        if (initialMessage) {
            initialMessage.remove(); // Remove a mensagem inicial "Comece uma conversa"
        }
        const messageElement = document.createElement("div");
        messageElement.className = "flex justify-end mb-4";
        messageElement.innerHTML = `
            <div class="bg-blue-600 text-white rounded-lg py-2 px-4 max-w-lg">
                ${message}
            </div>
        `;
        chatBox.appendChild(messageElement);
        scrollToBottom();
    }

    // Função para exibir a mensagem da IA (ou um erro)
    function displayAIMessage(data, isError = false) {
        const messageElement = document.createElement("div");
        messageElement.className = "flex justify-start mb-4";
        
        if (isError) {
            // Se for um erro, exibe apenas a mensagem de erro
            messageElement.innerHTML = `
                <div class="bg-red-500 text-white rounded-lg py-2 px-4 max-w-lg">
                    ${data.message}
                </div>
            `;
        } else {
            // Se for uma resposta bem-sucedida, formata com texto e metadados
            const bgColor = "bg-gray-700";
            // Substitui quebras de linha (\n) por tags <br> para uma exibição correta no HTML
            const formattedText = data.response_text.replace(/\n/g, '<br>');

            messageElement.innerHTML = `
                <div class="${bgColor} text-white rounded-lg py-2 px-4 max-w-lg">
                    <p>${formattedText}</p>
                    <div class="text-xs text-gray-400 mt-2 pt-2 border-t border-gray-600">
                        <span>Modelo: ${data.metadata.model}</span> | 
                        <span>Tokens: ${data.metadata.total_tokens}</span>
                    </div>
                </div>
            `;
        }
        
        chatBox.appendChild(messageElement);
        scrollToBottom();
    }

    // Função para mostrar o indicador de "digitando..."
    function showLoadingIndicator() {
        const loadingElement = document.createElement("div");
        loadingElement.id = "loading-indicator";
        loadingElement.className = "flex justify-start mb-4";
        loadingElement.innerHTML = `
            <div class="bg-gray-700 text-white rounded-lg py-2 px-4">
                <div class="flex items-center justify-center space-x-1">
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style="animation-delay: 0.2s;"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style="animation-delay: 0.4s;"></div>
                </div>
            </div>
        `;
        chatBox.appendChild(loadingElement);
        scrollToBottom();
    }
    
    // Função para remover o indicador de "digitando..."
    function removeLoadingIndicator() {
        const loadingIndicator = document.getElementById("loading-indicator");
        if (loadingIndicator) {
            loadingIndicator.remove();
        }
    }

    // Função principal para enviar a pergunta para a API
    async function sendQueryToAPI(query) {
        displayUserMessage(query);
        showLoadingIndicator();

        try {
            const response = await fetch('/api/generate-response/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken // Adiciona o token CSRF ao cabeçalho
                },
                body: JSON.stringify({ prompt: query })
            });

            removeLoadingIndicator();

            if (!response.ok) {
                const errorData = await response.json();
                // Tenta exibir um erro mais específico do serializer, se disponível
                const errorMessage = errorData.prompt ? errorData.prompt[0] : (errorData.error || "Ocorreu um erro na API.");
                throw new Error(errorMessage);
            }

            const data = await response.json();
            // Passa o objeto de dados completo para a função de exibição
            displayAIMessage(data);

        } catch (error) {
            console.error('Erro ao chamar a API:', error);
            removeLoadingIndicator();
            // Passa um objeto com a mensagem de erro para a função de exibição
            displayAIMessage({ message: `Erro: ${error.message}` }, true);
        }
    }

    // Adiciona o listener de eventos ao campo de input
    inputField.addEventListener("keydown", (event) => {
        // Verifica se a tecla pressionada é "Enter" e se o campo não está vazio
        if (event.key === "Enter" && inputField.value.trim() !== "") {
            const query = inputField.value.trim();
            inputField.value = ""; // Limpa o campo de input
            sendQueryToAPI(query);
        }
    });
});