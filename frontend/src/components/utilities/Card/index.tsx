import "./index.scss"

function Card () {
    return <>
        <div className="card">
            <div className="card-top-bar">
                <span className="card-discount">-30%</span>
                <button className="card-like" data-btn>
                    <svg viewBox="0 0 24 24">
                        <title>Like</title>
                        <use href="#icon-like-outline"></use>
                    </svg>
                </button>
            </div>

            <div className="card-image">
                <img src="/dummies/thumb-bananas.png" alt="Bananas" />
            </div>

            <h3 className="card-title">Bananas</h3>
            <span className="card-units">3 units</span>
            <strong className="card-price">$18.00</strong>


            <div className="card-bottom-bar">
                <div className="card-counter">
                    <button data-btn title="Remove Item" className="card-counter-btn">
                        <svg viewBox="0 0 24 24">
                            <title>Remove Item</title>
                            <use href="#icon-remove"></use>
                        </svg>
                    </button>

                    <em className="card-counter-count">3</em>

                    <button data-btn className="card-counter-btn">
                        {/* <span className="sr-only">Add Item</span> */}
                        <svg viewBox="0 0 24 24">
                            <title>Add Item</title>
                            <use href="#icon-add"></use>
                        </svg>
                    </button>
                </div>


                <button className="card-add-to-cart sr-only" data-btn>
                    Add to Cart
                </button>
            </div>

        </div>
    
    </>


}

export default Card