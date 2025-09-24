import { computed, map } from "nanostores"

interface CartItem {
    product_id: number
    price: number
    product_name: string
    count: number
}

export const $cart = map([] as CartItem[])
export const $cartIsEmpty = computed($cart, cart => cart.length === 0)
export const $cartTotal = computed($cart, cart => {
    let total = 0;

    cart.map(cartItem => {
        total += cartItem.count * cartItem.price 
    })

    return total
})

const searchForItemIndex = (product_id: number) => $cart.get().findIndex(cartItem => cartItem.product_id === product_id)

export const addItem = (product_id: number, product_name: string, price: number) => {
    const itemInCart = searchForItemIndex(product_id)

    console.log(itemInCart)

    if (itemInCart === -1) {
        const newCartItem: CartItem = {
            product_id,
            product_name,
            price,
            count: 1
        }

        $cart.set([...$cart.get(), newCartItem])
    }
    else {
        const cartItems = $cart.get()
        cartItems[itemInCart].count += 1

        console.log(cartItems[itemInCart])

        $cart.set([...cartItems])
    }

    console.log($cart.get())

    return 
}


export const removeItem = (product_id: number) => {
    const itemInCart = searchForItemIndex(product_id)    

    if (itemInCart === -1) {
        return
    }
    else {
        const cartItems = $cart.get()
        const itemCount = cartItems[itemInCart].count
        
        if (itemCount === 1) {
            $cart.set([...cartItems.filter(cartItem => cartItem.product_id !== product_id)])
        } else {
            cartItems[itemInCart].count -= 1;
            $cart.set([...cartItems])
        }
    }
}