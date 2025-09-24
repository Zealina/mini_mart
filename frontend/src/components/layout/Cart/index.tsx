import { useStore } from "@nanostores/react"
import { inactivateModal } from "../../../stores/modal"
import "./index.scss"
import { $cart, $cartTotal } from "../../../stores/cart"

export default function Cart() {

    const cart = useStore($cart);
    const cartTotal = useStore($cartTotal);

    return <>
        <section className="cart sgrid">
            <h2 className="cart-title">My Cart ({cart.length})</h2>
            <button className="cart-close" data-btn onClick={inactivateModal}>Close</button>


            <div className="cart-main">

                {cart.length ? 
                <>
                <dl className="cart-dl">
                    {
                        cart.map(cartItem => <>
                            <div className="cart-field">
                                <dt className="cart-item">{cartItem.product_name} ({cartItem.count})</dt>
                                <dd className="cart-price">₦{cartItem.count * cartItem.price}</dd>
                            </div>
                        </>)
                    }
                    <div className="cart-field">
                        <dt className="cart-item cart-total">Total</dt>
                        <dd className="cart-price cart-total">₦{cartTotal}</dd>
                    </div>
                </dl>

                <button className="cart-checkout-btn" data-btn>Go to Checkout</button>
                </>
                : 
                <>
                    <img className="cart-empty-image" src="/assets/empty-cart.svg" alt="Empty Cart" />
                    <p className="cart-empty-text">Cart is empty! Add items to buy</p>
                </> }
                
            </div>



        </section>

    </>
}