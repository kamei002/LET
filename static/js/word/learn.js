const app = new Vue({
    el: '#app',
    delimiters: ['${', '}'],
    data: {
        isChecked: false,
        id: 0,
      },
    methods: {
        sound(e) {
            e.currentTarget.querySelector("audio").play()
        },
        toggleVisible(e){
            elm = e.currentTarget.querySelector(".mean");
            elm.classList.toggle('hide');
        },
        toggleStar(e){

            const data = JSON.stringify({
                'is_checked': !this.isChecked,
                'word_summary_id': this.wordSummaryId
            });

            axios.post('http://localhost/word/api/star', data, this.ajaxConfig)
            .then(function(res){
                app.isChecked = res.data.is_checked
            })
            .catch(function(res){
                console.log(res)
            });
        },
        markedUnknown(){
            const data = JSON.stringify({
                'word_log_id': this.wordLogId
            });
            axios.post('http://localhost/word/api/unknown-word', data, this.ajaxConfig)
            .then(function(res){
                console.log(res)
                if(res.status === 200){
                    app.next()
                }
            })
            .catch(function(res){
                console.log(res)
            });
        },
        next(){
            location.reload();
        }
    },
    created: function(){
        const params = document.querySelector("#server_params");
        let isChecked = params.dataset.isChecked;
        this.isChecked = isChecked !== 'False';
        this.wordSummaryId =  params.dataset.wordSummaryId;
        this.wordLogId =  params.dataset.wordLogId;

        axios.defaults.xsrfCookieName = 'csrftoken'
        axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"
        this.ajaxConfig = {
            headers: {
                'Content-Type':'application/json',
                'Accept': 'application/json',
            },
            withCredentials:true,
        }
    }
})
