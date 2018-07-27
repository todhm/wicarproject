import * as basicAction from './actionType'
import {range} from '../utils/common/TimeUtil'
const thisYear = new Date().getFullYear()
const yearList = range(1885,thisYear);
export const CarBasicInfo ={
  address:{},
  addressError:"",
  yearError:"",
  year:"",
  yearList:yearList,
  brand:"",
  name:"",
  detail_address:"",
  transmission:"auto",
  valueObj:{},
  transJson:{"auto":"자동","manual":"수동"},
  cartype:"sedan",
  carTypeJson:[
      {label:"세단",value:"sedan"},
      {label:"쿠페",value:"cupe"},
      {label:"해치백",value:"hatchback"},
      {label:"컨버터블",value:"waegon"},
      {label:"트럭",value:"truck"},
      {label:"SUV",value:"suv"},
      {label:"RV",value:"rv"},
  ],
  transmissionList:[
      {label:"자동",value:"auto"},
      {label:"수동",value:"manual"},
  ],
  brandList:[],
  brandName:"",
  showClass:false,
  classList:[],
  className:"",
  showModel:false,
  modelList:[],
  model:"",
  brandError:"",
  distance:"",
  modelError:"",
  detailAddressError:"",
  insuranceError:"",
  insurance:"",
  carRegistered:false,
  is_active_car:false,
  carTypeError:"",
  transmissionError:"",
  advance_notice:"",
  advance_notice_label:"",
  advance_notice_error:"",
  description:"",
  description_error:"",
  price:"",
  price_error:"",
  plate_num:"",
  plate_num_error:"",
  roof_box:false,
  hid:false,
  led:false,
  auto_trunk:false,
  leather_seater:false,
  room_mirror:false,
  seat_6_4:false,
  seat_heater_1st:false,
  seat_heater_2nd:false,
  seat_cooler:false,
  high_pass:false,
  button_starter:false,
  handle_heater:false,
  premium_audio:false,
  hud:false,
  smart_cruz_control:false,
  tpms: false,
  curtton_airbag:false,
  esp:false,
  isofix:false,
  slope_sleepery:false,
  front_collusion:false,
  lane_alarm:false,
  high_bim:false,
  aux_bluetooth:false,
  usb:false,
  auto_head_light:false,
  android_conn:false,
  apple_conn:false,
  electric_brake:false,
  navigation:false,
  backword_cam:false,
  surround_view_cam:false,
  bolt_220:false,
  smartphone_charge:false,
  optionTypeList:[
      {typeLabel:"외관옵션",optionList:[{value:"roof_box",label:"루프박스"},
        {value:"hid",label:"HID 전조등"},{value:"led",label:"LED 전조등"},
        {value:"auto_trunk",label:"전동식 트렁크"}
      ]},
      {typeLabel:"내관옵션",optionList:[{value:"leather_seater",label:"가죽시트"},
        {value:"room_mirror",label:"눈부심방지 룸미러"},{value:"seat_heater_1st",label:"1열 열선시트"},
        {value:"seat_heater_2nd",label:"2열 열선시트"},{value:"seat_cooler",label:"통풍시트"},
        {value:"high_pass",label:"하이패스"},{value:"button_starter",label:"버튼시동"},
        {value:"handle_heater",label:"핸들열선"},{value:"premium_audio",label:"프리미엄 오디오"},
        {value:"hud",label:"HUD헤드업 디스플레이"},
      ]},
      {typeLabel:"안전사항",optionList:[{value:"smart_cruz_control",label:"스마트 크루즈 컨트롤"},
        {value:"tpms",label:"TPMS(타이어 공기압 측정)"},{value:"curtton_airbag",label:"커튼 에어백"},
        {value:"esp",label:"차체자세 제어장치(ESP,VSCM)"},{value:"isofix",label:"유아용 카시트 고정장치"},
        {value:"slope_sleepery",label:"경사로 밀림방지장치"},{value:"front_collusion",label:"전방충돌 보조장치"},
        {value:"lane_alarm",label:"차선이탈방지 보조시스템"},{value:"high_bim",label:"하이빔 보조시스템"},
      ]},
      {typeLabel:"편의사항",optionList:[{value:"aux_bluetooth",label:"AUX/Bluetooth"},
        {value:"usb",label:"USB 단자"},{value:"auto_head_light",label:"오토 헤드라이트"},
        {value:"android_conn",label:"안드로이드연동"},{value:"apple_conn",label:"애플연동"},
        {value:"electric_brake",label:"전자식 주차 브레이크"},{value:"navigation",label:"네비게이션"},
        {value:"backword_cam",label:"후방카메라"},{value:"surround_view_cam",label:"360도 서라운드 뷰 카메라"},
        {value:"bolt_220",label:"220볼트 단자"},{value:"smartphone_charge",label:"스마트폰 무선충전"},

      ]},
  ]

}



const CarBasicInfoReducer=(state=CarBasicInfo,action)=>{

    switch(action.type){
        default:
            return state

        case basicAction.CHANGE_VARIABLE:
                return {
                ...state,
                [action.name]:action.payload,
            }

        case basicAction.UPDATE_BASIC_SETTING:
                return {
                ...state,
                ...action.payload,
            }

    }
}

export default CarBasicInfoReducer;
