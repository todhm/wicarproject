import React, { Component } from 'react';
import {fetchCars,fetchBrands,filterCar} from './action'
import CarList from './CarList'
import {connect } from 'react-redux'
import SearchFilter from './SearchFilter'
import SearchRange from './SearchRange'

const initialState = {
      cartype:"",
      priceorder:"",
      brand:"",
      transmission:"",
      minPrice:5000,
      maxPrice:"",
      minDistance:0,
      maxDistance:"",
      minYear:1950,
      maxYear:"",
      moreFilter:false,
      maximumOverPrice:250000,
      maximumOverYear:2018,
      maximumOverDistance:1000,
}


const styles = {
    root: {
    },

  sidebar: {
    width: 256,
    height: '100%',
  },
  sidebarLink: {
    display: 'block',
    padding: '16px 0px',
    color: '#757575',
    textDecoration: 'none',
  },
  divider: {
    margin: '8px 0',
    height: 1,
    backgroundColor: 'black',
  },
  content: {
    padding: '16px',
    height: '100%',
    backgroundColor: 'white',
  },
};


class SideBarContent extends Component {

    state = initialState

    onSliderChange = (value,minState,maxState) => {
        (value[0]!==value[1])?
        this.setState((prevState)=>{
                    let newState={...prevState,
                                   [minState]:value[0],
                                   [maxState]:value[1],}
                   this.props.filterCar(newState.originalCarList,newState);
                    return newState
                   }):
        this.setState((prevState)=>{
                    let newState={
                                ...prevState,
                                [minState]:value[0],
                                [maxState]:"",
                            }
                     this.props.filterCar(newState.originalCarList,newState);
                     return newState})


    }
    componentDidMount(){
        this.props.getCarList().then((data)=>{
            this.setState({originalCarList: this.props.carList})
        })
        this.props.getBrandList()
    }


    handleInputChange = (e)=>{
            let name = e.target.name;
            let value = e.target.value;
            this.setState((prevState)=>{
                let newState = prevState;
                newState[name] = value
                this.props.filterCar(newState.originalCarList,newState);
                return newState
            });
        }
  render() {
      const { carList,cartypeList,priceOrderList,transmissionList,brandList,orderByPrice} = this.props;
      const {cartype,priceorder,brand,transmission} = this.state;

      return (
          <div  className="searchSideBarTop" style={styles.root}>
              <div className="searchSideBar">
                  <div className="searchSideBarSummary">
                      <div className="searchSideBarSummary-count">총{carList.length}대</div>
                  </div>
                  <form className="searchFiltersForm">
                      <SearchFilter
                          label="가격정렬"
                          name="priceorder"
                          optionList= {priceOrderList}
                          selectedOption={priceorder}
                          defaultLabel="가격정렬방식"
                          onChange={this.handleInputChange}
                          />

                      <SearchRange
                          initialMinState={initialState.minPrice}
                          initialMaxState={initialState.maxPrice}
                          minState={this.state.minPrice}
                          maxState={this.state.maxPrice}
                          minValue={5000}
                          maxValue={250000}
                          step={5000}
                          label={"가격범위"}
                          defaultLabel="전체가격"
                          rangeLabel={"₩" +this.state.minPrice +"-"+"₩" +this.state.maxPrice }
                          onSliderChange={(val)=>this.onSliderChange(val,"minPrice","maxPrice")}
                          />

                      {(this.state.moreFilter)?
                          <div className="collapsableBody-mask" >
                              <div className="collapsableBody-content">
                                  <SearchRange
                                      initialMinState={initialState.minDistance}
                                      initialMaxState={initialState.maxDistance}
                                      minState={this.state.minDistance}
                                      maxState={this.state.maxDistance}
                                      minValue={0}
                                      maxValue={1000}
                                      step={100}
                                      label={"일평균주행거리제한"}
                                      defaultLabel="전체거리"
                                      rangeLabel={this.state.minDistance+" km" +"-" +this.state.maxDistance+" km" }
                                      onSliderChange={(val)=>this.onSliderChange(val,"minDistance","maxDistance")}
                                      />

                                  <SearchRange
                                      initialMinState={initialState.minYear}
                                      initialMaxState={initialState.maxYear}
                                      minState={this.state.minYear}
                                      maxState={this.state.maxYear}
                                      minValue={1950}
                                      maxValue={2018}
                                      step={1}
                                      label={"차량연도"}
                                      defaultLabel="전체연도"
                                      rangeLabel={this.state.minYear+"-" +this.state.maxYear}
                                      onSliderChange={(val)=>this.onSliderChange(val,"minYear","maxYear")}
                                      />
                                  <SearchFilter
                                      label="차량종류"
                                      name="cartype"
                                      optionList= {cartypeList}
                                      selectedOption={cartype}
                                      defaultLabel="차량종류선택"
                                      onChange={this.handleInputChange}
                                      />
                                  <SearchFilter
                                      label="자동차브랜드"
                                      name="brand"
                                      optionList= {brandList}
                                      selectedOption={brand}
                                      defaultLabel="브랜드"
                                      onChange={this.handleInputChange}
                                      />
                                  <SearchFilter
                                      label="변속방식"
                                      name="transmission"
                                      optionList= {transmissionList}
                                      selectedOption={transmission}
                                      defaultLabel="변속방식"
                                      onChange={this.handleInputChange}
                                      />
                              </div>
                          </div>
                          :null
                      }

                      <div className="searchFiltersForm-actions">
                          <button className="button searchFiltersForm-toggleShow u-marginTop2 button--link" onClick={(e)=>this.setState({moreFilter:!this.state.moreFilter})} type="button">세부사항</button>
                      </div>
                  </form>
              </div>
          </div>
                );
  }
}

const mapStateToProps=({car_reducer,car_info})=>{
    return {
        ...car_reducer
    }
}

const mapDispatchToProps = (dispatch)=>{
    return {
        getCarList:()=>dispatch(fetchCars()),
        getBrandList:()=>dispatch(fetchBrands()),
        filterCar:(data,state)=>dispatch(filterCar(data,state))
    }
}

export default connect(mapStateToProps,mapDispatchToProps)(SideBarContent);
