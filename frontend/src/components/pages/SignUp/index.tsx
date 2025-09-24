import "./index.scss"


export function SignUp() {


    return <>


        <form id="signup-form" className="signup">
            <h1 className="signup-title">Sign Up Form</h1>

            <p>Required fields are followed by *</p>


            <section className="signup-section">

                <h2 className="signup-subtitle">Contact Information</h2>


                <div className="cinput-field">
                    <label htmlFor="">Name(s):</label>
                    <input type="text" name="first-name" placeholder="First Name *" required minLength={2} />
                    <input type="text" name="last-name" placeholder="Last Name *" required minLength={2} />
                    <input type="text" name="other-names" placeholder="Other Names" />
                </div>


                <div className="cinput-field">
                    <label htmlFor="">Email *</label>
                    <input type="email" name="email" placeholder="kincaid@gmail.com" required />
                </div>

                <div className="cinput-field">
                    <label htmlFor="">Adress</label>
                    <input type="text" name="adress" placeholder="18 Ifelodun Street, Abusoro, Akure." />
                </div>
            </section>




            <section className="signup-section">

                <h2 className="signup-subtitle">Accout Information</h2>

                <div className="cinput-field">
                    <label htmlFor="">Username *</label>
                    <input type="text" name="username" placeholder="kincaid_roy" required />
                </div>

                <div className="cinput-field">
                    <label htmlFor="">Password *</label>
                    <input type="password" name="adress" placeholder="Password" required minLength={8} />
                    <small>Password must be minimum of 6 letters</small>
                
                </div>
            </section>


            <input className="cinput-submit" id="signup-submit" type="submit" value="Sign Up" data-btn />
        </form>


    </>



}