import "./index.scss";

function Product() {
    return <>

        <section className="page-product">

            <div className="page-product-image">
                <img src="/dummies/thumb-bananas.png" alt="" />
            </div>


            <article className="page-product-copy">
                <span className="page-product-discount">30% off</span>
                <h1 className="page-product-title">Bananas</h1>
                <div className="page-product-description">
                    <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Dolor eveniet temporibus, illum mollitia voluptate tempore nesciunt qui laboriosam quam exercitationem!</p>
                </div>

                <p className="page-product-units">
                    <span className="sr-only">Units of Bananas Available:</span>
                    400 units
                </p>

                <strong className="page-product-price">
                    <span className="sr-only">Price of Bananas</span>
                    $154.00
                </strong>


                <div className="page-product-bottom-bar">
                    <button className="page-product-like" data-btn>

                        <svg viewBox="0 0 24 24">
                            <title>Like</title>
                            <use href="#icon-like-outline"></use>
                        </svg>

                    </button>


                    <div className="page-product-counter-bar">
                        <div className="page-product-counter sr-only">
                            <button data-btn title="Remove Item" className="page-product-counter-btn">
                                <svg viewBox="0 0 24 24">
                                    <title>Remove Item</title>
                                    <use href="#icon-remove"></use>
                                </svg>
                            </button>

                            <em className="page-product-counter-count">3</em>

                            <button data-btn className="page-product-counter-btn">
                                {/* <span className="sr-only">Add Item</span> */}
                                <svg viewBox="0 0 24 24">
                                    <title>Add Item</title>
                                    <use href="#icon-add"></use>
                                </svg>
                            </button>
                        </div>


                        <button className="page-product-add-to-cart " data-btn>
                            Add to Cart
                        </button>
                    </div>

                </div>


            </article>



        </section>

    </>
}


export default Product