export const AuthReducerToProps=({AuthReducer})=>{
    return {
        ...AuthReducer
    }
}

export const AdminReducerWithAuthToProps=({AdminReducer,AuthReducer})=>{
    return {
        AdminReducer,
        AuthReducer
    }
}

export const AdminReducerToProps=({AdminReducer})=>{
    return {
        ...AdminReducer
    }
}
