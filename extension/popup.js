async function load() {

    const status =
        document.getElementById("status");

    const button =
        document.getElementById("openCv");

    const tabs =
        await chrome.tabs.query({
            active: true,
            currentWindow: true
        });

    const tab = tabs[0];

    if (!tab || !tab.url) {

        status.textContent =
            "No se ha encontrado la URL.";

        return;
    }

    try {

        const response = await fetch(
            "http://127.0.0.1:8765/api/find?url=" +
            encodeURIComponent(tab.url)
        );

        const data =
            await response.json();

        if (!data.found) {

            status.textContent =
                "❌ No hay un CV generado para esta oferta.";

            return;
        }

        status.textContent =
            "✅ CV encontrado\n" +
            data.title +
            " — " +
            data.company;

        button.style.display =
            "block";

        button.onclick = () => {

            const cvUrl =
                "http://127.0.0.1:8765/" +
                data.cv;

            chrome.tabs.create({
                url: cvUrl
            });
        };

    } catch (error) {

        status.textContent =
            "⚠️ JobHunter no está ejecutándose.";
    }
}


load();