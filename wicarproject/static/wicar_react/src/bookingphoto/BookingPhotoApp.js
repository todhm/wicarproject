import React, {Component, Fragment} from 'react';
import {Link} from 'react-router-dom'
import {Route} from 'react-router-dom'
import PropTypes from 'prop-types'
import RegisterPic, {dataURItoBlob, readFileAsDataURL} from '../registerpic/RegisterPic'
import Cropper from 'react-cropper';
import 'cropperjs/dist/cropper.css';
import Modal from 'react-modal'
import Loading from 'react-loading'
import AddPhoto from './AddPhoto'
import EditPhoto from './EditPhoto'
import PhotoAlbum from './photoAlbum'
import * as RegisterApi from '../utils/RegisterApi'
import '../car_regist.css'

// using ES6 modules
const inputStyle = {
    position: "absolute",
    right: "0px",
    top: "0px",
    fontFamily: "Arial",
    fontSize: "118px",
    margin: "0px",
    padding: "0px",
    cursor: "pointer",
    opacity: 0,
    height: "100%"
}
const spanStyle = {
    position: "relative",
    overflow: "hidden",
    direction: "ltr"
}

var appElement = document.getElementById('root');
Modal.setAppElement(appElement);

export default class extends Component {

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
            is_active_car: false,
            booking_id: "",
            description: "",
            src: ""
        }

        this.cropImage = this.cropImage.bind(this);
        this.handleFileChange = this.handleFileChange.bind(this);
    }

    handleFileChange = (event) => {
        this.setState({loadingImage: true})
        const file = event.target.files[0]
        if (file && file.type.match(/^image\//)) {
            if (file.size > 10000000) {
                this.setState({imageError: "10mb 이상의 파일은 등록할 수 없습니다.", loadingImage: false})
                return;
            }
            readFileAsDataURL(file).then(originalURL => {
                this.setState({src: originalURL, uploadImage: true, loadingImage: false, imageError: ""})
            })
        } else {
            this.setState({imageError: "알맞은 형식이 아닙니다.", loadingImage: false})
        }
    }

    cropImage = (e) => {
        this.setState({loadingImage: true})
        if (typeof this.cropper.getCroppedCanvas() === 'undefined') {
            this.setState({imageError: "이미지를 선택해주세요.", loadingImage: false})
            return;
        }
        var dataURL = this.cropper.getCroppedCanvas().toDataURL();
        this.setState({cropResult: dataURL, uploadImage: false, loadingImage: false})

    }

    sendBookingImage = () => {
        if (this.state.cropResult) {
            var blob = dataURItoBlob(this.state.cropResult);
        } else {
            this.setState({imageError: "이미지를 업로드해주세요."})
            return;
        }
        var formData = new FormData();
        formData.append("image", blob);
        this.setState({loadingImage: true})
        var booking_id = this.state.booking_id;
        formData.append('description', this.state.description)
        RegisterApi.addBookingImage(formData, booking_id).then((data) => {
            if (data.message == "success") {
                this.setState(prevState => {
                    var oldImgList = prevState.urlList;
                    oldImgList.push(data)
                    return {
                        urlList: oldImgList,
                        imageError: "",
                        cropResult: "",
                        description: "",
                        uploadImage: false,
                        loadingImage: false,
                        image_index: false
                    }
                })
            } else {
                this.setState({
                    imageError: "파일사이즈가 맞지 않습니다.",
                    cropResult: "",
                    description: "",
                    uploadImage: false,
                    loadingImage: false,
                    image_index: false
                })
            }
        }).catch((error) => {
            this.setState({imageError: "전송에러가발생했습니다.", uploadImage: false, loadingImage: false})
        })
    }

    componentDidMount = () => {
        var pathList = this.context.router.history.location.pathname.split("/", -1)
        var bookingId = (pathList.length >= 3)
            ? pathList[pathList.length - 1]
            : "";
        this.setState({booking_id: bookingId})
        RegisterApi.getBookingImage(bookingId).then(data => {
            if (data.message == "success") {
                this.setState({urlList: data.urlList})
            }
        })
    }

    handleDescription = (e) => {
        this.setState({description: e.target.value});
    }

    closeModal = () => {
        this.setState({uploadImage: false})
    }

    render() {
        const divStyle = this.state.cropResult
            ? {
                backgroundImage: `url(${this.state.cropResult})`
            }
            : null
        const nodeFunc = node => this.fileInput = node;
        const {urlList, imageError, description} = this.state;
        return (<div id="pageContainer-content" className="u-contentTopPadding u-contentBottomPadding">
            <Fragment>
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
                                            }} minCropBoxWidth={200} minCropBoxHeight={200} aspectRatio={400 / 400} preview=".img-preview" guides={false} src={this.state.src} ref={cropper => {
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
            </Fragment>
            <div id="trip-photos" className="container ">
                <h5>사진등록</h5>
                <p>여행전과 여행 후의 차량상태 오도미터 기름계기판 등을 체크해주세요.</p>
                {
                    (this.state.loadingImage)
                        ? <Loading delay={200} type='spin' color='#222' className='loading'/>
                        : null
                }
                <span className="errorMessage-text">{imageError}</span>
                <div className="photo-uploader grid">
                    {
                        this.state.cropResult
                            ? <EditPhoto divStyle={divStyle} nodeFunc={nodeFunc} handleFileChange={this.handleFileChange} inputStyle={inputStyle}/>
                            : <AddPhoto spanStyle={spanStyle} nodeFunc={nodeFunc} handleFileChange={this.handleFileChange} inputStyle={inputStyle}/>
                    }
                    <div className="description-and-share grid-item grid-item--9">
                        <div className="grid">
                            <div className="grid-item grid-item--12">
                                <textarea className="description" value={description} onChange={this.handleDescription} name="description" maxLength="10000" placeholder="사진에 대한 설명을 적어주세요."></textarea>
                            </div>
                            <div className="grid-item grid-item--12">
                                <div className="buttonWrapper buttonWrapper--baseTopMargin">
                                    <button onClick={this.sendBookingImage} className="js-shareButton share-button u-truncate button button--green ">
                                        사진등록하기
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                {
                    urlList.length > 0
                        ? <Fragment>
                                <div className="subheader">사진목록</div>
                                <div className="js-myPhotos photos-section">
                                    <ul>
                                        {urlList.map((url) => (<PhotoAlbum key={url.url} photoData={url}/>))}
                                    </ul>
                                </div>
                            </Fragment>
                        : null
                }
            </div>
        </div>)
    }
}
