const API_URL = "/api";

const app = {
    activeTaskId: null,
    pollingInterval: null,

    init() {
        console.log("AI Text Helper готов к работе");
        this.loadExample();
    },

    async checkAsync() {
        const textInput = document.getElementById("textInput");
        const resultArea = document.getElementById("resultArea");

        const text = textInput.value.trim();

        if (!text) {
            this.showToast("Введите текст для обработки", "warning");
            return;
        }

        resultArea.innerHTML = `
            <div class="task-status">
                ⏳ Задача отправляется в очередь...
            </div>
        `;

        try {
            const response = await fetch(`${API_URL}/tasks`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    text: text,
                    mode: "fix"
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Не удалось создать задачу");
            }

            this.activeTaskId = data.task_id;

            resultArea.innerHTML = `
                <div class="task-status">
                    ✅ Задача создана<br>
                    <small>ID: ${data.task_id.slice(0, 8)}...</small><br>
                    <div id="taskStatus">⏳ Ожидание обработки...</div>
                </div>
            `;

            this.showToast("Задача отправлена в очередь", "info");
            this.startPolling(data.task_id);

        } catch (error) {
            resultArea.innerHTML = `
                <div class="task-status">
                    ❌ Ошибка: ${error.message}
                </div>
            `;
            this.showToast("Ошибка подключения к серверу", "error");
        }
    },

    async checkSpelling() {
        await this.checkAsync();
    },

    startPolling(taskId) {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }

        this.pollingInterval = setInterval(() => {
            this.checkTaskStatus(taskId);
        }, 1500);

        this.checkTaskStatus(taskId);
    },

    async checkTaskStatus(taskId) {
        const resultArea = document.getElementById("resultArea");
        const statusDiv = document.getElementById("taskStatus");

        try {
            const response = await fetch(`${API_URL}/tasks/${taskId}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Не удалось получить статус задачи");
            }

            if (data.status === "queued") {
                if (statusDiv) {
                    statusDiv.textContent = "⏳ Задача находится в очереди...";
                }
            }

            if (data.status === "processing" || data.status === "started") {
                if (statusDiv) {
                    statusDiv.textContent = "⚙️ Текст обрабатывается worker-сервисом...";
                }
            }

            if (data.status === "done") {
                clearInterval(this.pollingInterval);
                this.pollingInterval = null;

                this.displayResults(data.result);
                this.showToast("Обработка завершена", "success");
            }

            if (data.status === "failed") {
                clearInterval(this.pollingInterval);
                this.pollingInterval = null;

                resultArea.innerHTML = `
                    <div class="task-status">
                        ❌ Ошибка обработки: ${data.error || "Неизвестная ошибка"}
                    </div>
                `;

                this.showToast("Ошибка обработки", "error");
            }

        } catch (error) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;

            resultArea.innerHTML = `
                <div class="task-status">
                    ❌ Ошибка: ${error.message}
                </div>
            `;

            this.showToast("Ошибка подключения к серверу", "error");
        }
    },

    displayResults(result) {
        const resultArea = document.getElementById("resultArea");

        resultArea.innerHTML = `
            <div class="result-area">
                <h3>Результат обработки</h3>
                <div class="result-text">${this.escapeHtml(result)}</div>
            </div>
        `;
    },

    clearText() {
        document.getElementById("textInput").value = "";
        document.getElementById("resultArea").innerHTML = "";
        this.showToast("Поле очищено", "info");
    },

    loadExample() {
        const textInput = document.getElementById("textInput");

        if (!textInput) {
            return;
        }

        textInput.value = `привет это тестовый текст который нужно улучшить и исправить`;
        this.showToast("Пример загружен", "success");
    },

    showToast(message, type = "info") {
        const toast = document.createElement("div");
        toast.textContent = message;

        Object.assign(toast.style, {
            position: "fixed",
            bottom: "20px",
            right: "20px",
            padding: "12px 20px",
            borderRadius: "12px",
            color: "white",
            background:
                type === "success"
                    ? "#16a34a"
                    : type === "error"
                    ? "#dc2626"
                    : type === "warning"
                    ? "#d97706"
                    : "#2563eb",
            zIndex: "1000",
            boxShadow: "0 10px 30px rgba(0,0,0,0.2)",
            fontSize: "14px",
            fontWeight: "600"
        });

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    },

    escapeHtml(text) {
        return String(text)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;")
            .replaceAll("\n", "<br>");
    }
};

document.addEventListener("DOMContentLoaded", () => app.init());