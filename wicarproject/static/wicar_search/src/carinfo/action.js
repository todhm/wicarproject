import {getCarImages,getCarInfo} from '../utils/api'
import moment from 'moment';
import 'moment/locale/ko';

export const FETCH_CAR_IMAGES = 'FETCH_CAR_IMAGES'
export const FETCH_CAR_INFO='FETCH_CAR_INFO'
export const FETCH_BOOKING_START='FETCH_BOOKING_START'
export const FETCH_BOOKING_END='FETCH_BOOKING_END'
export const HANDLE_TIME_CHANGE="HANDLE_TIME_CHANGE";

export const recieveImages=(imageList)=>({
    type:FETCH_CAR_IMAGES,
    imageList,
})

export const recieveCarInfo=(carInfoData)=>({
    type:FETCH_CAR_INFO,
    carInfoData,
})

export const recieveBookingStart=(bookingStartStr)=>({
    type:FETCH_BOOKING_START,
    bookingStartStr,
})
export const recieveBookingEnd=(bookingEndStr)=>({
    type:FETCH_BOOKING_END,
    bookingEndStr,
})

export const fetchImages=(car_id)=>dispatch=>(
    getCarImages(car_id).then(response=>{
        if(response.data.message==="success"){
            return dispatch(recieveImages(response.data.imgList.map((x)=>x.url)))
        }
        else{
            return dispatch(recieveImages([]))
        }
    })
);
export const handleTimeChange = (bookingStartTime,bookingEndTime) => ({
	type: HANDLE_TIME_CHANGE,
	bookingStartTime,
	bookingEndTime,
})

const optionLabelList ={roof_box :"루프박스",
                    hid      :"HID 전조등",
                    led      :"LED 전조등",
                    auto_trunk :"전동식 트렁크",
                    leather_seater  :"가죽시트",
                    room_mirror   :"눈부심방지 룸미러",
                    seat_heater_1st :"1열 열선시트",
                    seat_heater_2nd :"2열 열선시트",
                    seat_cooler:"통풍시트",
                    high_pass:"하이패스",
                    button_starter:"버튼시동",
                    handle_heater:"핸들열선",
                    premium_audio:"프리미엄 오디오",
                    hud:"HUD헤드업 디스플레이",
                    smart_cruz_control:"스마트 크루즈 컨트롤",
                    tpms:"TPMS(타이어 공기압 측정)",
                    curtton_airbag:"커튼 에어백",
                    esp:"차체자세 제어장치(ESP,VSCM)",
                    isofix:"유아용 카시트 고정장치",
                    slope_sleepery:"경사로 밀림방지장치",
                    front_collusion:"전방충돌 보조장치",
                    lane_alarm:"차선이탈방지 보조시스템",
                    high_bim:"하이빔 보조시스템",
                    aux_bluetooth:"AUX/Bluetooth",
                    usb:"USB 단자",
                    auto_head_light:"오토 헤드라이트",
                    android_conn:"안드로이드 연동",
                    apple_conn:"애플 연동",
                    electric_brake:"전자식 주차 브레이크",
                    navigation:"네비게이션",
                    backword_cam:"후방카메라",
                    surround_view_cam:"360도 서라운드 뷰 카메라",
                    bolt_220:"220볼트 단자",
                    smartphone_charge:"스마트폰 무선 충전"}



export const fetchCarInfo=(car_id)=>dispatch=>(
    getCarInfo(car_id).then(response=>{
        const carinfo = response.data
        carinfo['description'] = carinfo['caroption']['description']
        carinfo['price'] = carinfo['caroption']['price']
        let optionList=[]
        Object.keys(optionLabelList).forEach(function(key,index) {
            if(carinfo['caroption'][[key]]){
                optionList.push(optionLabelList[key])
            }
        });
        if (carinfo['bookingStartTime']){
            carinfo['bookingStartTime']= moment(carinfo['bookingStartTime'], 'MM-DD-YYYY HH:mm')
            carinfo['bookingEndTime']= moment(carinfo['bookingEndTime'], 'MM/DD/YYYY HH:mm')
        }
        else{
            carinfo['bookingEndTime'] = moment().add(8, 'd').hours(10).minutes(0);
            carinfo['bookingStartTime']=moment().add(1, 'd').hours(10).minutes(0);
        }
        carinfo['optionList'] = optionList
        return dispatch(recieveCarInfo(carinfo))
    })
)
