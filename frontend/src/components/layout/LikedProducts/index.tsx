import { inactivateModal } from "../../../stores/modal"
import Card from "../../utilities/Card"
import "./index.scss"


export default function LikedProducts() {

    return <>
        <section className="liked-products sgrid">
            <button title="Close" className="liked-products-close" data-btn onClick={inactivateModal}>Close</button>
            <h2 className="liked-products-title">Liked Products (3)</h2>
            <div className="liked-products-main">
                <ul className="liked-products-list">
                    <li className="liked-products-list"><Card isLikeComponent={true} /></li>
                    <li className="liked-products-list"><Card isLikeComponent={true} /></li>
                    <li className="liked-products-list"><Card isLikeComponent={true} /></li>
                    <li className="liked-products-list"><Card isLikeComponent={true} /></li>
                </ul>
            </div>
        </section>


    </>

}