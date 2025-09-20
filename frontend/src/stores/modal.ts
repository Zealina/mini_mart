import { atom } from "nanostores";

export const $modalIsActive = atom(false);
const modalIsActiveClass = "modal-is-active"


$modalIsActive.subscribe(modalIsActive => {
    const isInBrowser = "document" in globalThis;
    if (!isInBrowser) return

    const bodyElement = globalThis.document.body
    
    if (modalIsActive) {
        bodyElement.classList.add(modalIsActiveClass)
    } else {
        bodyElement.classList.remove(modalIsActiveClass)
    }

})


export const activateModal = () => { $modalIsActive.set(true) }
export const inactivateModal = () => { $modalIsActive.set(false) }
