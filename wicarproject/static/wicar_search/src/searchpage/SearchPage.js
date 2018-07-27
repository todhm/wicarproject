import React, { Component } from 'react';
import {fetchCars,fetchBrands,filterCar} from './action'
import CarList from './CarList'
import SideBarContent from './SideBarContent'
import {connect } from 'react-redux'
import {get_car_list} from '../utils/api'
import Slider, { Range } from 'rc-slider';
import SearchFilter from './SearchFilter'
import SearchRange from './SearchRange'
import Sidebar from 'react-sidebar';


const mql = window.matchMedia(`(min-width: 950px)`);


class SearchPage extends Component {


       state = {
         mql: mql,
         docked: false,
         open: false,
         styles: {
             root: {
                 position:"fixed",
                 overflowY: 'auto',
                 top:"100000000000px"
             },

         sidebar: {
             zIndex: 2,
             position: 'fixed',
             backgroundColor:"white",
             bottom: 0,
             transition: 'transform .3s ease-out',
             WebkitTransition: '-webkit-transform .3s ease-out',
             willChange: 'transform',
             overflowY: 'auto',
             width:"260px",
           },
           content: {
             position: 'relative',
             top: 0,
             right: 0,
             bottom: 0,
             overflowY: 'auto',
             WebkitOverflowScrolling: 'touch',
             transition: 'left .3s ease-out, right .3s ease-out',
           },
         overlay: {
             zIndex: 1,
             overflowY: 'auto',
             position: 'absolute',
             top: 0,
             right: 0,
             bottom: 0,
             opacity: 0,
             visibility: 'hidden',
             transition: 'opacity .3s ease-out, visibility .3s ease-out',
             backgroundColor: 'rgba(0,0,0,.3)',

           },
           dragHandle: {
             zIndex: 1,
             overflowY: 'auto',
             position: 'absolute',
             top: 210,
             bottom: 0,
             left: "350px",

           },
         },
       }





     componentWillMount() {
       mql.addListener(this.mediaQueryChanged);
       this.setState((prevState)=>{
           let styles = this.state.styles

           if(mql.matches){
               let sidebar = styles.sidebar
               sidebar['top']  ='100px'
               sidebar['marginLeft'] = '7%'
               styles['sidebar'] = sidebar


           }
           return {mql: mql, docked: mql.matches,styles:styles}
       });


     }

     componentWillUnmount() {
       this.state.mql.removeListener(this.mediaQueryChanged);
     }

     onSetOpen=(open)=> {
         this.setState((prevState)=>{
             let styles = prevState.styles;
             let rootStyle = prevState.styles.root;
             rootStyle['zIndex']=0
             rootStyle['top'] ="100000000000px"
             styles['root'] = rootStyle
             return {open: open, styles:styles}
         });
     }

     mediaQueryChanged=()=>{
     this.setState((prevState)=>{
         let styles = this.state.styles

         if(mql.matches){
             let sidebar = styles.sidebar
             sidebar['top']  ='100px'
             sidebar['marginLeft'] = '7%'
             styles['sidebar'] = sidebar


         }
         else{
             let sidebar = styles.sidebar
             sidebar['top']  =0
             sidebar['marginLeft'] = 0
             styles['sidebar'] = sidebar
         }
         return {mql: mql, docked: this.state.mql.matches,styles:styles}
     });

       this.setState({
         mql: mql,
         docked: this.state.mql.matches,
        });
     }

     toggleOpen=(e)=> {
       this.setState((prevState)=>{
           let styles = prevState.styles;
           let rootStyle = prevState.styles.root;
           let prevOpen = prevState.open;
           if(!prevOpen){
               rootStyle['top']=0
               rootStyle['zIndex']=4
           }
           else{
               rootStyle['zIndex']=0
           }
           styles['root'] = rootStyle
           return {open: !prevOpen, styles:styles}
       });
     }


      render() {
          const { carList} = this.props;
          const sidebar = <SideBarContent />;
          const sidebarProps = {
            sidebar: sidebar,
            docked: this.state.docked,
            open: this.state.open,
            onSetOpen: this.onSetOpen,
            styles:this.state.styles,
          };

          return (

        <div className="pageContainer" >
            <div className="searchFilterButton">
                    {(!mql.matches && !this.state.open)?
                        <div aria-label="Active view" className="buttonGroup searchToggle" role="group">
                            <button className="button button--green is-active" type="button" onClick={this.toggleOpen} >
                                <span className="button-iconContainer">
                                    <span className="searchToggle-icon searchToggle-icon--list"></span>
                                </span>차량검색
                            </button>
                        </div>:
                        null
                    }
                <Sidebar {...sidebarProps}>
                </Sidebar>
            </div>
            <div className="searchResultsList" >
                <div aria-busy="false">
                    <div aria-label="grid" aria-readonly="true" className="ReactVirtualized__Grid ReactVirtualized__List" role="grid" tabIndex="0" >
                        <div className="ReactVirtualized__Grid__innerScrollContainer" role="rowgroup" >
                            <CarList/>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        );
      }
    }

const mapStateToProps=({car_reducer,CarInfoReducer,BookingPageReducer})=>{
    return {
        ...car_reducer
    }
}




export default connect(mapStateToProps)(SearchPage);
