import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import PropTypes from 'prop-types'
import serializeForm from 'form-serialize'
import SmallField from '../SmallField'
import * as RegisterApi from '../utils/RegisterApi'
import Picture from './Picture';
import './picture.css'
import Cropper from 'react-cropper';
import 'cropperjs/dist/cropper.css';
import Modal from 'react-modal'


const uplaodstyle = {height: '140px'}
const overlayStyle = {
    position: "relative",
    overflow: "hidden",
    direction: "ltr"
}



const inputStyle={
    position: "absolute",
    right: "0px",
    top: "0px",
    "font-family": "Arial",
    "font-size": "118px",
    margin: "0px",
    padding: "0px",
    cursor: "pointer",
    opacity: 0,
    height: "100%"
}

const divStyle={
    height:"140px"
}




class ImageInput extends Component{



    static contextTypes = {
       router: PropTypes.object
     }

     state = {
         uploadImage:false,
         src:"",
     }


     handleModal=(e)=>{
         this.setState({uploadImage:true})
     }
     closeModal=()=>{
         this.setState({uploadImage:false})
     }





    render(){


    const { urlList, removeImage,handleFileChange,imageError,loadingImage } = this.props;
    let totalListNum = urlList.length >=4 ? urlList.length : 4;
        return(
            <section className="section section--first">
                <h5>사진 등록하기</h5>
                <div>고객님의 차량을 마음껏 뽐내보세요. 차량 등록을 위해서 최소 앞뒤좌우 4면의  사진이 필요합니다.</div>
                <div className="section section--withSmallMargin text--small">
                    <span id="photo-uploader-status">640x320이상의 이미지가 필요합니다.</span>
                </div>
                <div className="section section--withSmallMargin">
                    <div id="listing-vehicle-photo-uploader" className="photoUploader" style={divStyle}>
                        <div id="upload-photos-items-wrapper" >
                            <ul className="items ui-sortable">
                                 {[...Array(totalListNum)].map((x,index)=>{
                                     return urlList.length < index +1?
                                          <Picture  index={index} key={index} />
                                         :<Picture index={index}  key={index} removeImage={removeImage} val={urlList[index]} loadingImage={loadingImage}/>
                                     })}
                                <li className="uploader vehiclePhoto vehiclePhoto--small" >
                                    <div className="upload upload--withOverlay" style={overlayStyle} >
                                        <div className="upload-default">
                                            <div className="icon"></div>
                                            <div>사진 추가</div>
                                        </div>
                                        <input  ref={node => this.fileInput = node}
                                                className="pictureButton"
                                                 multiple="true"
                                                 accept="image/*"
                                                 type="file"
                                                 name="file"
                                                 onChange={handleFileChange}/>
                                    </div>
                                    <span className="errorMessage-text">{imageError}</span>
                                </li>
                            </ul>
                        </div>
                        <div className="spacer"></div>
                    </div>
                </div>
                <Modal
                    className='modal'
                    overlayClassName='overlay'
                    isOpen={this.state.uploadImage}
                    onRequestClose={this.closeIngredientsModal}
                    contentLabel='Modal'
                    >
                    <div>
                        <Cropper
                                 style={{ height: 400, width: '100%' }}
                                 aspectRatio={16 / 9}
                                 preview=".img-preview"
                                 guides={false}
                                 src={this.state.src}
                                 ref={cropper => { this.cropper = cropper; }}
                               />
                    </div>
                </Modal>

            </section>

        )
    }
}




export default ImageInput;
