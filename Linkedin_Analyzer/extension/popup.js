document
    .getElementById("analyze")
    .addEventListener("click", async () => {

        const resultElement = document.getElementById("result");
        const errorElement = document.getElementById("error");
        const statusElement = document.getElementById("status");

        const percentageElement = document.getElementById("percentage");
        const progressBar = document.getElementById("progress-bar");
        const resultMessage = document.getElementById("result-message");

        try {

            statusElement.classList.remove("hidden");
            resultElement.classList.add("hidden");
            errorElement.classList.add("hidden");


            const tabs = await chrome.tabs.query({
                active: true,
                currentWindow: true
            });

            const tab = tabs[0];


            // ESTA PARTE ES EXACTAMENTE LA ORIGINAL

            const response = await chrome.tabs.sendMessage(
                tab.id,
                {
                    action: "getJobDescription"
                }
            );


            if (!response || !response.description) {

                throw new Error(
                    "No se ha encontrado la descripción de la oferta."
                );
            }


            // ESTA PARTE TAMBIÉN ES LA ORIGINAL

            const heraclesResponse = await fetch(
                "http://127.0.0.1:8000/analyze",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        description: response.description
                    })
                }
            );


            if (!heraclesResponse.ok) {

                throw new Error(
                    `HTTP ${heraclesResponse.status}`
                );
            }


            const result = await heraclesResponse.json();


            // AQUÍ CAMBIA SOLAMENTE LA PRESENTACIÓN

            const score = result.match_percentage;

            percentageElement.textContent = score;

            progressBar.style.width = `${score}%`;


            if (score >= 80) {

                resultMessage.textContent =
                    "La oferta cumple tu umbral de compatibilidad.";

            } else {

                resultMessage.textContent =
                    "La oferta no alcanza tu umbral de compatibilidad.";
            }


            statusElement.classList.add("hidden");
            resultElement.classList.remove("hidden");


        } catch (error) {

            statusElement.classList.add("hidden");

            errorElement.textContent =
                "❌ " + error.message;

            errorElement.classList.remove("hidden");
        }

    });