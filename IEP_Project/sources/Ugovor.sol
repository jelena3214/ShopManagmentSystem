pragma solidity ^0.8.2;

contract DeliveryContract {
    address payable public owner;
    address payable public courier;
    address payable public customer;
    uint public totalAmount;
    bool public isDelivered;
    bool public isCourierAssigned;
    bool public isPaid;

    constructor(address payable _customer, address payable _owner, uint _totalAmount) {
        require(_totalAmount > 0, "Total amount must be greater than zero.");
        owner = _owner;
        customer = _customer;
        isCourierAssigned = false;
        isDelivered = false;
        totalAmount = _totalAmount;
        isPaid = false;
    }

    function pay(address payable  _customer) external payable onlyBeforeDelivery{
        require(!isPaid, "Already paid");
        require(_customer == customer, "Not the right customer address!");
        require(msg.value == totalAmount, "You have to transfer the exact amount!");
        isPaid = true;
    }

    function assignCourier(address payable _courier) external onlyBeforeDelivery{
        require(!isCourierAssigned, "Courier is already assigned");
        require(isPaid, "Order is not paid");

        courier = _courier;
        isCourierAssigned = true;
    }

    function getCourierAssigned() external view returns(bool){
        return isCourierAssigned;
    }

    function getCourier() external view returns(address){
        return courier;
    }

    function getBalance() external view returns(uint){
        return address(this).balance;
    }

    function confirmDelivery() external onlyBeforeDelivery{
        require(msg.sender == customer, "Only the right customer can confirm delivery");
        require(isPaid, "Not paid");
        require(isCourierAssigned, "Courier is not assigned");

        uint courierAmount = (address(this).balance * 20) / 100;
        owner.transfer(address(this).balance - courierAmount);
        courier.transfer(courierAmount);

        isDelivered = true;
    }

    modifier onlyBeforeDelivery() {
        require(!isDelivered, "Interaction is not allowed after delivery.");
        _;
    }
}
