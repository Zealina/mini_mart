import { inactivateModal } from "../../../stores/modal"
import "./index.scss"

export default function Cart() {

    return <>
        <section className="cart">
            <h2 className="cart-title">My Cart (3)</h2>
            <button className="cart-close" data-btn onClick={inactivateModal}>Close</button>


            <dl className="cart-dl">
                <title>Cart Items and their Prices</title>
                <div className="cart-field">
                    <dt className="cart-item">Oranges (2)</dt>
                    <dd className="cart-price">$10</dd>
                </div>

                <div className="cart-field">
                    <dt className="cart-item">Mangos (2)</dt>
                    <dd className="cart-price">$14</dd>
                </div>

                <div className="cart-field">
                    <dt className="cart-item">Bananas (2)</dt>
                    <dd className="cart-price">$10</dd>
                </div>


                <div className="cart-field">
                    <dt className="cart-item cart-total">Total</dt>
                    <dd className="cart-price cart-total">$34</dd>
                </div>
            </dl>

            <button className="cart-checkout-btn" data-btn>Go to Checkout</button>



        </section>

    </>
}