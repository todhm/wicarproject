import React from 'react'


export default ({nodeFunc,handleFileChange,inputStyle,spanStyle})=>(
    <div className="js-addPhotoContainer add-photo-container grid-item grid-item--2">
        <span
             className="js-addPhotoButton addTripPhotoButton  qq-upload-button-hover"
              style={spanStyle}
              >
            <span className="content">
                <span className="icon"></span>
                <span className="text">사진올리기</span>
            </span>
            <input id="temp-image"
                ref={nodeFunc}
                qq-button-id="6c8b0056-928c-47c0-a992-fff3798afe3f"
                 accept="image/*"
                 type="file" name="file"
                 style={inputStyle}
                 onChange={handleFileChange}/>
         </span>
    </div>
)
