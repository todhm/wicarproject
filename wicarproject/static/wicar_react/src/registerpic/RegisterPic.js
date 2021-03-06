import React, {Component} from 'react';
import {Link} from 'react-router-dom'
import PropTypes from 'prop-types'
import serializeForm from 'form-serialize'
import SmallField from '../SmallField'
import ImageInput from './ImageInput'
import * as RegisterApi from '../utils/RegisterApi'
import './picture.css'
import Picture from './Picture';
import Cropper from 'react-cropper';
import 'cropperjs/dist/cropper.css';
import Modal from 'react-modal'
import Loading from 'react-loading'

const uplaodstyle = {
    height: '140px'
}
const overlayStyle = {
    position: "relative",
    overflow: "hidden",
    direction: "ltr"
}

const inputStyle = {
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

const divStyle = {
    height: "140px"
}

export const dataURItoBlob = (dataURI) => {
    // convert base64/URLEncoded data component to raw binary data held in a string
    var byteString;
    if (dataURI.split(',')[0].indexOf('base64') >= 0) 
        byteString = atob(dataURI.split(',')[1]);
    else 
        byteString = unescape(dataURI.split(',')[1]);
    
    // separate out the mime component
    var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];

    // write the bytes of the string to a typed array
    var ia = new Uint8Array(byteString.length);
    for (var i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }

    return new Blob([ia], {type: mimeString});
}

export const readFileAsDataURL = (file) => new Promise(resolve => {
    const reader = new FileReader()

    reader.onload = (event) => {
        resolve(event.target.result)
    }

    reader.readAsDataURL(file)
})

var appElement = document.getElementById('root');
Modal.setAppElement(appElement);

class RegisterPic extends Component {

    static contextTypes = {
        router: PropTypes.object
    }

    constructor(props) {
        super(props);
        this.state = {
            value: '',
            urlList: [],
            imageError: "",
            loadingImage: false,
            uploadImage: false,
            cropResult: "",
            image_index: false,
            is_active_car: false
        }

        this.cropImage = this.cropImage.bind(this);
    }

    componentDidMount = () => {
        var pathList = this.context.router.history.location.pathname.split("/", -1)
        var carid = (pathList.length >= 3)
            ? pathList[pathList.length - 1]
            : "";
        RegisterApi.getCarImages(carid).then((data) => {
            if (data.message == "success") 
                this.setState({urlList: data.imgList, is_active_car: data.active})
        });
    }

    updateFileChange = (image_index) => {
        this.setState({image_index: image_index})
        this.fileInput.click();

    }

    handleFileChange = (event) => {
        const file = event.target.files[0]
        if (file && file.type.match(/^image\//)) {
            if (file.size > 10000000) {
                this.setState({imageError: "10mb 이상의 파일은 등록할 수 없습니다.", image_index: false})
                return;
            }
            readFileAsDataURL(file).then(originalURL => {
                this.setState({src: originalURL, uploadImage: true})
            })
        } else {
            this.setState({imageError: "알맞은 형식이 아닙니다.", image_index: false})
        }
    }

    closeModal = () => {
        this.setState({uploadImage: false})
    }

    cropImage = (e) => {
        if (typeof this.cropper.getCroppedCanvas() === 'undefined') {
            return;
        }
        var pathList = this.context.router.history.location.pathname.split("/", -1)
        var carid = (pathList.length >= 3)
            ? pathList[pathList.length - 1]
            : "";
        var dataURL = this.cropper.getCroppedCanvas().toDataURL();
        var blob = dataURItoBlob(dataURL);
        var formData = new FormData();
        formData.append("image", blob);
        this.setState({loadingImage: true})
        if (typeof this.state.image_index === 'number' && !isNaN(this.state.image_index)) {
            formData.append('image_index', this.state.image_index)
            RegisterApi.updateCarImage(formData, carid).then((data) => {
                if (data.message == "success") {
                    this.setState({urlList: data.imgList, imageError: "", uploadImage: false, loadingImage: false, image_index: false})
                } else {
                    this.setState({imageError: "640x320이상의 이미지를 사용해주세요", uploadImage: false, loadingImage: false, image_index: false})
                }
            }).catch((error) => {
                this.setState({imageError: "전송에러가발생했습니다.", uploadImage: false, loadingImage: false, image_index: false})
            })
        } else {
            RegisterApi.addCarImage(formData, carid).then((data) => {
                if (data.message == "success") {
                    this.setState({urlList: data.imgList, imageError: "", uploadImage: false, loadingImage: false, image_index: false})
                } else {
                    this.setState({imageError: "640x320이상의 이미지를 사용해주세요", uploadImage: false, loadingImage: false, image_index: false})
                }
            }).catch((error) => {
                this.setState({imageError: "전송에러가발생했습니다.", uploadImage: false, loadingImage: false, image_index: false})
            })
        }
    }

    removeImage = (e, index) => {
        let data = {};
        data['image_index'] = index;
        var pathList = this.context.router.history.location.pathname.split("/", -1)
        var carid = (pathList.length >= 3)
            ? pathList[pathList.length - 1]
            : "";
        RegisterApi.removeCarImage(data, carid).then((data) => {
            if (data.message == "success") 
                this.setState({urlList: data.imgList, imageError: ""})
            else 
                this.setState({imageError: "삭제를 실패하였습니다. 다시 시도해주세요."})

        })
    }

    handleSubmit = (e) => {
        e.preventDefault()
        if (this.state.urlList.length >= 4) {
            var pathList = this.context.router.history.location.pathname.split("/", -1)
            var carid = (pathList.length >= 3)
                ? pathList[pathList.length - 1]
                : "";
            if (this.state.is_active_car) {
                window.location.href = "/get_car_list"
            } else {
                window.location.href = "/confirm_car" + "/" + carid;
            }
        } else {
            this.setState({imageError: "차량등록을 위해선 최소 4장의 사진이 필요합니다."})
        }
    }

    backPage = () => {
        var pathList = this.context.router.history.location.pathname.split("/", -1)
        var carid = (pathList.length >= 3)
            ? pathList[pathList.length - 1]
            : "";
        return "/time_price" + "/" + carid;
    }

    render() {

        const {urlList, imageError, loadingImage} = this.state;
        let totalListNum = urlList.length >= 4
            ? urlList.length
            : 4;
        return (<div id="driver-approval">
            <Modal className='Modal__Bootstrap modal-dialog' overlayClassName='overlay' isOpen={this.state.uploadImage} onRequestClose={this.closeModal} contentLabel='Modal'>
                {
                    (this.state.loadingImage)
                        ? <Loading delay={200} type='spin' color='#222' className='loading'/>
                        : <div className="modal-content">
                                <div className="modal-header">
                                    <button type="button" className="close" onClick={this.closeModal}>
                                        <span aria-hidden="true">&times;</span>
                                        <span className="sr-only">Close</span>
                                    </button>
                                </div>
                                <div className="modal-body">

                                    <Cropper style={{
                                            width: '100%',
                                            maxHeight: '300px'
                                        }} minCropBoxWidth={400} minCropBoxHeight={200} aspectRatio={640 / 320} preview=".img-preview" guides={false} src={this.state.src} ref={cropper => {
                                            this.cropper = cropper;
                                        }}/>
                                </div>
                                <div className="modal-footer">
                                    <button type="button" className="btn btn-secondary" onClick={this.closeModal}>취소</button>
                                    <button type="button" className="btn btn-primary" onClick={this.cropImage}>사진저장하기</button>
                                </div>
                            </div>
                }

            </Modal>
            <div id="images-and-instructions" className="listing_content">
                <form id="list-vehicle" onSubmit={this.handleSubmit}>
                    <div id="images">
                        <section className="section section--first">
                            <h5>사진 등록하기</h5>
                            <div>고객님의 차량을 마음껏 뽐내보세요. 차량 등록을 위해서 최소 앞뒤좌우 4면의 사진이 필요합니다.</div>
                            <div className="section section--withSmallMargin text--small">
                                <span id="photo-uploader-status">640x320이상의 이미지가 필요합니다.</span>
                            </div>
                            <div className="section section--withSmallMargin">
                                <div id="listing-vehicle-photo-uploader" className="photoUploader" style={divStyle}>
                                    <div id="upload-photos-items-wrapper">
                                        <ul className="items ui-sortable">
                                            {
                                                [...Array(totalListNum)].map((x, index) => {
                                                    return urlList.length < index + 1
                                                        ? <Picture imageIndex={index} key={index}/>
                                                        : <Picture imageIndex={urlList[index].image_index} key={index} removeImage={this.removeImage} updateImage={this.updateFileChange} val={urlList[index].url}/>
                                                })
                                            }
                                            <li className="uploader vehiclePhoto vehiclePhoto--small">
                                                <div className="upload upload--withOverlay" style={overlayStyle}>
                                                    <div className="upload-default">
                                                        <div className="icon"></div>
                                                        <div>사진 추가</div>
                                                    </div>
                                                    <input ref={node => this.fileInput = node} className="pictureButton" multiple="true" accept="image/*" type="file" name="file" onChange={this.handleFileChange}/>
                                                </div>
                                                <span className="errorMessage-text">{imageError}</span>
                                            </li>
                                        </ul>
                                    </div>
                                    <div className="spacer"></div>
                                </div>
                            </div>
                        </section>
                        <div className="buttonWrapper buttonWrapper--noTopMargin">
                            <Link to={this.backPage()} id="back" className="button">이전</Link>
                            <button className="submit button button--purple" type="submit">다음</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>)
    }
}

export default RegisterPic;
