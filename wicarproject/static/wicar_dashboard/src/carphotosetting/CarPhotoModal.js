import React,{Component} from 'react';
import {
    Dialog,
    DialogActions,
    DialogContent,
    Grid,
    DialogContentText,
    DialogTitle,
    TextField,
    Button,
    Input,
    InputLabel,
    InputAdornment,
    Typography
} from '@material-ui/core';
import DatePicker from 'react-datepicker';
import moment from 'moment';
import 'moment/locale/ko'
import 'react-datepicker/dist/react-datepicker.css';
import {withStyles} from '@material-ui/core/styles';
import styles from '../utils/styles/styles'
import classNames from 'classnames';
import Loading from 'react-loading'
import Cropper from 'react-cropper';

const  CarPhotoModal=(props)=>{

    const{cropImage,close,loadingImage,closeModal,src,classes,uploadImage} = props;
    return(
        <Dialog open={uploadImage} onClose={closeModal} fullWidth={true} aria-labelledby="form-dialog-title" >
            <DialogTitle id="form-dialog-title">"사진등록"</DialogTitle>
                <DialogContent classes={{root:classes.dialogStyle}} style={{height:500}}>
                    <Grid container>
                        {
                        (loadingImage)
                            ? <Loading delay={200} type='spin' color='#222' className='loading'/>
                            :
                                <Cropper style={{
                                        width: '100%',
                                        maxHeight: '300px'
                                    }} minCropBoxWidth={400} minCropBoxHeight={200} aspectRatio={640 / 320} preview=".img-preview" guides={false} src={src} ref={cropper => {
                                        this.cropper = cropper;
                                    }}/>
                        }
                    </Grid>
                </DialogContent>
                <DialogActions>
                    <Button onClick={closeModal} color="primary">
                        취소
                    </Button>
                    <Button type="submit" color="primary " onClick={this.cropImage}>사진저장하기</Button>
                </DialogActions>
        </Dialog>
        )
}

export default withStyles(styles)(CarPhotoModal);
