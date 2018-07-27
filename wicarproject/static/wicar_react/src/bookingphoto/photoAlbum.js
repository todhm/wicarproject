import React from 'react'


export default ({photoData})=>(
    <li>
        <div className="trip-photo" data-id="8788930">
            <a className="dialog-link" href={"/car_info/" + photoData.car_id}>
                <span className="image-container">
                    <img src={photoData.url} alt=""/>
                    <span className="overlay"></span>
                </span>
                <span className="narrow-details">
                    <span className="description-and-created">
                        <span className="created text--small">{photoData.sender_name+" "+ photoData.dateString}</span>
                    </span>
                </span>
            </a>
            <div className="details">
                <div className="created text--small">
                    <a className="text--purple" href={"/user_info/" + photoData.sender_id}>{photoData.sender_name}</a>
                    <span>{photoData.dateString}</span>
                </div>
            </div>
        </div>
    </li>
)
