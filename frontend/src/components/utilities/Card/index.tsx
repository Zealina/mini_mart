import { $cart, addItem, removeItem } from "../../../stores/cart"
import "./index.scss"
import { useStore } from "@nanostores/react"

// TODO: remove this
const DUMMY_CARD = {
    product_id: 2021,
    product_name: "Banana",
    package_size: "3 ounces",
    price: 40,
    image: "/dummies/thumb-bananas.png"
}


function Card({ isLikeComponent = false, productData = DUMMY_CARD }) {

    const cart = useStore($cart)
    const isInCart = cart.find(item => item.product_id === productData.product_id)


    return <>
        <div className="card">
            <div className="card-top-bar">
                {
                    isLikeComponent ?
                        <></> :
                        <button className="card-like" data-btn>
                            <svg viewBox="0 0 24 24">
                                <title>Like</title>
                                <use href="#icon-like-outline"></use>
                            </svg>
                        </button>
                }
            </div>

            <div className="card-image">
                <img src={productData.image} alt={productData.product_name} />
            </div>

            <h3 className="card-title">{productData.product_name}</h3>
            <span className="card-units">{productData.package_size}</span>
            <strong className="card-price">₦{productData.price}</strong>


            <div className="card-bottom-bar">

                {isInCart ?
                    <div className="card-counter">
                        <button data-btn title="Remove Item" className="card-counter-btn"
                        onClick={removeItem.bind(null, productData.product_id)}>
                            <svg viewBox="0 0 24 24">
                                <title>Remove Item</title>
                                <use href="#icon-remove"></use>
                            </svg>
                        </button>

                        <em className="card-counter-count">{isInCart.count ?? 0}</em>

                        <button data-btn className="card-counter-btn" 
                        onClick={addItem.bind(null, productData.product_id, productData.product_name, productData.price)}>
                            {/* <span className="sr-only">Add Item</span> */}
                            <svg viewBox="0 0 24 24">
                                <title>Add Item</title>
                                <use href="#icon-add"></use>
                            </svg>
                        </button>
                    </div>
                    :


                    <button className="card-add-to-cart" data-btn onClick={
                        addItem.bind(null, productData.product_id, productData.product_name, productData.price)
                        }>
                        Add to Cart
                    </button>
                }
            </div>

        </div>

    </>


}

export default Card