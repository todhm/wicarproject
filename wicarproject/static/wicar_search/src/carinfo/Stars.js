import React from 'react';





const Stars=(props)=>{
    const {reviewRate} = props
    return(
        <div className="starRating-rating starRating-rating--large starRating-rating--purple">
           { [...Array(parseInt(reviewRate)).keys()].map((num)=>(
               <span className="starRating-star starRating-star--filled" key={num}></span>
           ))}
            {(reviewRate - parseInt(reviewRate) >= 0.7)?
              <span className="starRating-star starRating-star--filled"></span>
             :(reviewRate - parseInt(reviewRate) < 0.7 && reviewRate - parseInt(reviewRate) >= 0.3)?
             <span className="starRating-star starRating-star--halfFilled"></span>
             :null
            }
        </div>

    )
}

export default Stars
