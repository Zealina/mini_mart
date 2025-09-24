import { inactivateModal } from "../../../stores/modal"
import Card from "../../utilities/Card"
import "./index.scss"



export default function SearchBar() {

    return <>
        <section className="search-bar sgrid">
            <button title="Close" className="search-bar-close" data-btn onClick={inactivateModal}>Close</button>
            <h2 className="search-bar-title">Search Bar</h2>
            <div className="search-bar-main">
                <form className="search-bar-form">
                    <input className="search-bar-input" type="text" name="search-bar-text" placeholder="Search for products. .e.g banana" />

                </form>

                <ul className="search-bar-list">
                    <li className="search-bar-list"><Card /></li>
                    <li className="search-bar-list"><Card /></li>
                    <li className="search-bar-list"><Card /></li>
                    <li className="search-bar-list"><Card /></li>
                </ul>


                <a href="#" data-btn className="search-bar-link">See More Products</a>
            </div>
        </section>


    </>


}