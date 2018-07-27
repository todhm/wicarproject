import React from 'react';
import PropTypes from 'prop-types'
import './picture.css'


const overlayStyle = {
    position: "relative",
    overflow: "hidden",
    direction: "ltr"
}

const Picture=props=>{


    let {imageIndex,val,removeImage,updateImage} = props;

    let is_val = typeof val!=="undefined"? true:false;
    return(
        <li className="uploaded vehiclePhoto vehiclePhoto--small" key={imageIndex}>
            {
             (is_val)?
                  <div key={imageIndex}>
                      <img onClick={(e)=>updateImage(imageIndex)} src={val} className="media media--fluid" />
                      {(imageIndex >=4)?
                      <a className="delete-button" onClick={(e)=> removeImage(e,imageIndex)}>
                          <span className="icon"></span>
                          <span className="confirm text--small">삭제하시겠습니까?</span>
                      </a>
                      :null}

                  </div>
                  :<img className="media media--fluid" key={imageIndex}/>
             }
             {  imageIndex===0? <div className="media-overlay">전방이미지</div>
               :imageIndex===1? <div className="media-overlay">후방이미지</div>
               :imageIndex===2? <div className="media-overlay">우측이미지</div>
               :imageIndex===3? <div className="media-overlay">좌측이미지</div>
               :null}
         </li>
    )

}




Picture.propTypes = {
   imageIndex: PropTypes.number.isRequired,
   removeImage: PropTypes.func,
   val:PropTypes.string
 }


export default Picture;
