import React from 'react'


export default ({divStyle,nodeFunc,handleFileChange,inputStyle})=>(
    <div className="js-addPhotoContainer add-photo-container grid-item grid-item--2 preview">
        <div className="js-photoPreviewContainer photo-preview-container" style={divStyle}>
            <div className="photo-placeholder">
                <span className="icon"></span><span className="text"></span>
            </div>
            <div className="change-photo">
                <span id="change-photo-button" className="js-changePhotoButton button small">사진교체
                <input id="temp-image"
                    ref={nodeFunc}
                    qq-button-id="6c8b0056-928c-47c0-a992-fff3798afe3f"
                     accept="image/*"
                     type="file" name="file"
                     style={inputStyle}
                     onChange={handleFileChange}/>
                </span>
            </div>
        </div>
    </div>

)
