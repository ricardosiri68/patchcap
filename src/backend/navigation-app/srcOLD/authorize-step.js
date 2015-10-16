class AuthorizeStep {
    run(routingContext, next) {
        if (routingContext.nextInstructions.some(i => i.config.auth)) {
            var isLoggedIn = AuthorizeStep.isLoggedIn();
            if (!isLoggedIn) {
                alert("Not Logged In!\nClick the Sign In icon to log in");
                return next.cancel();
            }
        }
        return next();
    }
 
    static isLoggedIn(): boolean {
        var auth_token = true;//localStorage.getItem("auth_token");
        return (typeof auth_token !== "undefined" && auth_token !== null);
    }
}