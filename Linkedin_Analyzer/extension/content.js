function getJobDescription() {

    const descriptionElement = document.querySelector(
        '[data-testid="expandable-text-box"]'
    );

    if (!descriptionElement) {
        return null;
    }

    return descriptionElement.innerText;
}


chrome.runtime.onMessage.addListener(
    (message, sender, sendResponse) => {

        if (message.action === "getJobDescription") {

            const description = getJobDescription();

            sendResponse({
                description: description
            });
        }

    }
);