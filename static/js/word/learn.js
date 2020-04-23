const app = new Vue({
    el: '#app',
    methods: {
        sound(e) {
            e.currentTarget.querySelector("audio").play()
        },
        toggleVisible(e){
            elm = e.currentTarget.querySelector(".mean");
            console.log(elm);
            elm.classList.toggle('hide');
        }
    },
})