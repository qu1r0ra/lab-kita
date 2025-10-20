const listContainer = document.querySelector("#list-items-container")

//SEARCH LOGIC
const searchBar = document.querySelector("#search-bar")

searchBar.value = ""
let copyOfList

searchBar.addEventListener("input", (e) => {
    if (searchBar.value) {
        if (listContainer.dataset.version === "original") {
            copyOfList = Array.from(listContainer.children).map(child => child.cloneNode(true));
        }
        listContainer.dataset.version = "copy"
        listContainer.innerHTML = ""

        const searchResult = searchArticles(searchBar.value)
        searchResult.forEach(item => {
            listContainer.append(item)
        })

    } else {
        listContainer.dataset.version = "original"
        listContainer.innerHTML = ""
        copyOfList.forEach(item => {
            listContainer.append(item)
        })
    }
})

const searchArticles = (query) => {
    let queriedItems = []
    query = query.toLowerCase()

    copyOfList.forEach(article => {
        title = article.querySelector(".article").textContent.toLowerCase()
        if (title.includes(query)) {
            queriedItems.push(article)
        }
    })

    return queriedItems
}

listContainer.addEventListener("click", (e) => {
    if (e.target.classList.contains("duplicate-icon")) {
        if (listContainer.dataset.version === "original") { //copy to copyList while duplicating in original
            copyOfList = Array.from(listContainer.children).map(child => child.cloneNode(true));
        } else if (listContainer.dataset.version === "copy") { //copy to original while duplicating during search
            duplicateItem(e.target.parentNode.parentNode, "copy")
        }
    }

    if (e.target.className.includes("delete-icon")) {
        if (listContainer.dataset.version === "original") {
            copyOfList = Array.from(listContainer.children).map(child => child.cloneNode(true));
        }
    }
})

// DUPLICATE, DELETE, and CONFIRMATION LOGIC
const modalContainer = document.querySelector('#modal-overlay');
const modalBox = document.querySelector("#modal")
const yes = document.querySelector("#confirmation-yes")
const no = document.querySelector("#confirmation-no")

listContainer.addEventListener("click", (e) => {
    if (e.target.className.includes("duplicate-icon")) {
        actionController(e, duplicateItem, "duplicate") //confirm and duplicate
    }

    if (e.target.className.includes("delete-icon")) { //confirm and delete
        actionController(e, deleteItem, "delete")
    }
})

const actionController = (e, func, action) => {
    const element = e.target.parentNode.parentNode //get element
    const articleTitle = element.querySelector(".article-item") //get title 
    const actionName = document.querySelector("#action-container-span")
    const popupArticleName = document.querySelector("#article-title-span")

    actionName.textContent = action
    popupArticleName.textContent = articleTitle.textContent //assign title to popup
    modalContainer.classList.remove('hidden'); //show popup

    modalContainer.addEventListener('click', w => {
        if (w.target === yes) {
            func(element, "original")
            modalContainer.classList.add('hidden');
        } else if (w.target === no) {
            modalContainer.classList.add('hidden');
        }
        else if (w.target === modalContainer) {
            modalContainer.classList.add('hidden');
        }
    }, { once: true })
}

const duplicateItem = (originalItem, version) => {
    if (version === "original") {
        const copyOfItem = originalItem.cloneNode(true)
        let title = copyOfItem.querySelector(".article")
        title.textContent = `Copy of ${title.textContent.trim()}`
        listContainer.insertBefore(copyOfItem, originalItem)
    } else if (version === "copy") {
        const copyOfItem = originalItem.cloneNode(true)
        let title = copyOfItem.querySelector(".article")
        title.textContent = `Copy of ${title.textContent}`
        copyOfList.splice(copyOfList.indexOf(originalItem) + 1, 0, copyOfItem)
    }
}

const deleteItem = (item, version) => {
    if (version === "original")
        listContainer.removeChild(item)
    else if (version === "copy")
        copyOfList.removeChild(item)
}

// CHANGING STATUS LOGIC
listContainer.addEventListener("click", (e) => {
    const element = e.target

    if (element.className.includes("status-info")) {
        changeStatus(element)
    }
})

const changeStatus = (status) => {
    console.log(status.classList)
    if (status.classList.contains("finished")) {
        status.style.backgroundColor = "#CD3546"
        status.textContent = "Unfinished"
        status.classList.replace("finished", "unfinished")
    } else if (status.classList.contains("unfinished")) {
        status.style.backgroundColor = "#52914E"
        status.textContent = "Finished"
        status.classList.replace("unfinished", "finished")
    }
    console.log(status.classList)
}