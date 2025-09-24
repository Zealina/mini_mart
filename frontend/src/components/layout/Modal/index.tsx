import "./index.scss"
import Cart from "../Cart"
import LikedProducts from "../LikedProducts"
import SearchBar from "../SearchBar"

export default function Modal() {


    // Make the modal close when the target of the click event is the modal itself!
    return <>
        <section className="c-modal" id="modal" aria-hidden="false">
            <Cart />
            {/* <LikedProducts /> */}
            {/* <SearchBar /> */}
        </section>
    
    
    </>
}