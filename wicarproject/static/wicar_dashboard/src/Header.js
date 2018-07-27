import React from 'react';



export const Header=(props)=>{
    const{currentLink} = props;
    let settingClass;
    let settingCurrent;
    let settingHref;
    let carListClass;
    let carListCurrent;
    let carListHref;
    currentLink === "car_owner_setting"?(
        settingClass =  "navbarLink navbarLink--active",
        settingCurrent = "true",
        settingHref="#",
        carListClass = "navbarLink",
        carListCurrent = "false",
        carListHref="/get_car_list"
    ):(
        settingClass =  "navbarLink",
        settingCurrent = "false",
        settingHref="/car_owner_setting",
        carListClass = "navbarLink navbarLink--active",
        carListCurrent = "true",
        carListHref="#"
    )



    return(
        <div className="pageContainer pageContainer--fluid">
            <div className="pageContainer u-backgroundColorBlackLight u-boxShadow pageContainer--fluid">
                <div className="pageContainer navbar">
                    <div className="navbar-links">
                        <a className={carListClass} aria-current={carListCurrent} href={carListHref}>차고</a>
                        <a className="navbarLink" aria-current="false" href="/notifications">알림</a>
                        <a className="navbarLink" aria-current="false" href="/owner_review">리뷰</a>
                        <a className="navbarLink" aria-current="false" href="/earning">수익</a>
                        <a className={settingClass} aria-current={settingCurrent} href={settingHref}>설정</a>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Header;
