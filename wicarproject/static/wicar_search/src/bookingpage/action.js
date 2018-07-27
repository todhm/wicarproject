
export const CHANGE_INSURANCE = "CHANGE_INSURANCE"
export const CHANGE_MONTH = "CHANGE_MONTH"
export const CHANGE_YEAR = "CHANGE_YEAR"




export const changeInsurance=(insuranceName)=>({
    type:CHANGE_INSURANCE,
    insuranceName,
})


export const changeYear=(expire_year)=>({
    type:CHANGE_YEAR,
    expire_year,
})

export const changeMonth=(expire_month)=>({
    type:CHANGE_MONTH,
    expire_month,
})
