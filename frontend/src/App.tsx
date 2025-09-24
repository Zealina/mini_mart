import "./styles/App.scss"
import Card from "./components/utilities/Card"
import Product from "./components/pages/Product"
import Modal from "./components/layout/Modal"
import { $modalIsActive, activateModal } from "./stores/modal"
import { useStore } from "@nanostores/react"
import { SignUp } from "./components/pages/SignUp"
import { $cart } from "./stores/cart"

function App() {
  const modalIsActive = useStore($modalIsActive)
  const cart = useStore($cart)


  return (
    <>
      <header className="header" aria-hidden={modalIsActive} inert={modalIsActive}>
        <div className="header-logo">
          <img src="/dummies/logo.png" alt="Logo" className="header-logo-img" />
        </div>
        <nav className="header-nav">
          <ul className="header-nav-list">
            <li className="header-nav-li">
              <button data-btn className="header-nav-search-btn">
                <span>Search</span>

                <svg viewBox="0 0 24 24">
                  <use href="#icon-search"></use>
                </svg>
              </button>
            </li>
            <li className="header-nav-li">
              <button data-btn className="header-nav-liked-products">
                  <span>Liked Products</span>
                <svg viewBox="0 0 24 24">
                  <use href="#icon-like-outline"></use>
                </svg>
              </button>  
            </li>
            <li className="header-nav-li">
              <a href="#" data-btn className="header-nav-sign-in">Sign In</a>
            </li>
            <li className="header-nav-li">
              <button data-btn className="header-nav-cart" onClick={activateModal}>
                <svg viewBox="0 0 24 24">
                  <use href="#icon-cart"></use>
                </svg>
                <span>Cart ({cart.length})</span>

              </button> 
            </li>
          </ul>

        </nav>
      </header>
      <main className="main sgrid" aria-hidden={modalIsActive} inert={modalIsActive}>


        <SignUp />

        <Product />        

        {/* TODO: remove the inline styles */}
        <section style={{marginTop: "3rem"}} className="products">
          <h2 className="products-title">Trending Products</h2>


          <ul className="products-list">
            <li className="products-li"><Card/></li>
            <li className="products-li"><Card/></li>
            <li className="products-li"><Card/></li>
            <li className="products-li"><Card/></li>
          </ul>
        </section>





      </main>
      <footer className="footer" aria-hidden={modalIsActive} inert={modalIsActive}></footer>

      <Modal />



      <svg style={{display: "none"}}>
        <symbol viewBox="0 0 24 24" id="icon-like-outline">
          <path fill="currentColor" d="m12 21l-1.45-1.3q-2.525-2.275-4.175-3.925T3.75 12.812T2.388 10.4T2 8.15Q2 5.8 3.575 4.225T7.5 2.65q1.3 0 2.475.55T12 4.75q.85-1 2.025-1.55t2.475-.55q2.35 0 3.925 1.575T22 8.15q0 1.15-.387 2.25t-1.363 2.412t-2.625 2.963T13.45 19.7zm0-2.7q2.4-2.15 3.95-3.687t2.45-2.675t1.25-2.026T20 8.15q0-1.5-1-2.5t-2.5-1q-1.175 0-2.175.662T12.95 7h-1.9q-.375-1.025-1.375-1.687T7.5 4.65q-1.5 0-2.5 1t-1 2.5q0 .875.35 1.763t1.25 2.025t2.45 2.675T12 18.3m0-6.825"></path>
        </symbol>

        <symbol viewBox="0 0 24 24" id="icon-add">
          <path fill="currentColor" d="M11 13H5v-2h6V5h2v6h6v2h-6v6h-2z"></path>
        </symbol>

        <symbol viewBox="0 0 24 24" id="icon-remove">
          <path fill="currentColor" d="M5 13v-2h14v2z"></path>
        </symbol>

        <symbol viewBox="0 0 24 24" id="icon-search">
          <path fill="currentColor" d="m19.6 21l-6.3-6.3q-.75.6-1.725.95T9.5 16q-2.725 0-4.612-1.888T3 9.5t1.888-4.612T9.5 3t4.613 1.888T16 9.5q0 1.1-.35 2.075T14.7 13.3l6.3 6.3zM9.5 14q1.875 0 3.188-1.312T14 9.5t-1.312-3.187T9.5 5T6.313 6.313T5 9.5t1.313 3.188T9.5 14"></path>
        </symbol>

        <symbol viewBox="0 0 24 24" id="icon-person-outline">
          <path fill="currentColor" d="M9.775 12q-.9 0-1.5-.675T7.8 9.75l.325-2.45q.2-1.425 1.3-2.363T12 4t2.575.938t1.3 2.362l.325 2.45q.125.9-.475 1.575t-1.5.675zm0-2h4.45L13.9 7.6q-.1-.7-.637-1.15T12 6t-1.263.45T10.1 7.6zM4 20v-2.8q0-.85.438-1.562T5.6 14.55q1.55-.775 3.15-1.162T12 13t3.25.388t3.15 1.162q.725.375 1.163 1.088T20 17.2V20zm2-2h12v-.8q0-.275-.137-.5t-.363-.35q-1.35-.675-2.725-1.012T12 15t-2.775.338T6.5 16.35q-.225.125-.363.35T6 17.2zm6 0"></path>
        </symbol>

        <symbol viewBox="0 0 24 24" id="icon-cart">
          <path fill="currentColor" d="M7 22q-.825 0-1.412-.587T5 20t.588-1.412T7 18t1.413.588T9 20t-.587 1.413T7 22m10 0q-.825 0-1.412-.587T15 20t.588-1.412T17 18t1.413.588T19 20t-.587 1.413T17 22M5.2 4h14.75q.575 0 .875.513t.025 1.037l-3.55 6.4q-.275.5-.737.775T15.55 13H8.1L7 15h12v2H7q-1.125 0-1.7-.987t-.05-1.963L6.6 11.6L3 4H1V2h3.25z"></path>
        </symbol>


      </svg>
    </>
  )
}

export default App

