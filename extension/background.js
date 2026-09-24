async function checkTab(tabId, url) {

    if (!url || !url.startsWith("http")) {
        return;
    }

    try {

        const response = await fetch(
            "http://127.0.0.1:8765/api/find?url=" +
            encodeURIComponent(url)
        );

        if (!response.ok) {
            return;
        }

        const data = await response.json();

        if (data.found) {

            chrome.action.setBadgeText({
                tabId: tabId,
                text: "CV"
            });

            chrome.action.setTitle({
                tabId: tabId,
                title:
                    "CV disponible: " +
                    data.title
            });

        } else {

            chrome.action.setBadgeText({
                tabId: tabId,
                text: ""
            });

            chrome.action.setTitle({
                tabId: tabId,
                title: "JobHunter CV"
            });
        }

    } catch (error) {

        chrome.action.setBadgeText({
            tabId: tabId,
            text: ""
        });
    }
}


chrome.tabs.onUpdated.addListener(
    (tabId, changeInfo, tab) => {

        if (
            changeInfo.status === "complete" &&
            tab.url
        ) {

            checkTab(
                tabId,
                tab.url
            );
        }
    }
);


chrome.tabs.onActivated.addListener(
    async (activeInfo) => {

        const tab = await chrome.tabs.get(
            activeInfo.tabId
        );

        if (tab.url) {

            checkTab(
                tab.id,
                tab.url
            );
        }
    }
);