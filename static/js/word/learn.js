const app = new Vue({
    el: '#app',
    delimiters: ['${', '}'],
    data: {
        errorAnswer: false,
        isChecked: false,
        meanHide: true,
        id: 0,
      },
    methods: {
        sound(e) {
            e.currentTarget.querySelector("audio").play()
        },
        toggleVisible(){
            this.meanHide = !this.meanHide
        },
        toggleStar(e){

            const data = JSON.stringify({
                'is_checked': !this.isChecked,
                'word_summary_id': this.wordSummaryId
            });

            axios.post('/word/api/star', data, this.ajaxConfig)
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
            axios.post('/word/api/unknown-word', data, this.ajaxConfig)
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
            if(this.hasErrorAnswer()){
                return
            }
            // location.reload();
            const url = `/word/learn?index=${app.index+1}&category_id=${app.categoryId}`
            location.replace(url)
        },
        hasErrorAnswer(){
            this.errorAnswer = false;
            let answer = this.$refs["answer"].value
            if(!answer){
                return false
            }
            answer = answer.trim()

            if(!answer){
                return false
            }
            if(answer === this.word){
                return false
            }
            console.log("wrong Answer")
            this.errorAnswer = true;
            return true

        },
    },
    created: function(){
        const params = document.querySelector("#server_params");
        let isChecked = params.dataset.isChecked;
        this.isChecked = isChecked !== 'False';
        this.wordSummaryId =  params.dataset.wordSummaryId;
        this.wordLogId =  params.dataset.wordLogId;
        this.word =  params.dataset.wordWord;
        this.categoryId =  params.dataset.categoryId;
        this.index = Number(params.dataset.index);

        axios.defaults.xsrfCookieName = 'csrftoken'
        axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"
        this.ajaxConfig = {
            headers: {
                'Content-Type':'application/json',
                'Accept': 'application/json',
            },
            withCredentials:true,
        }
    },
    mounted: function(){
        $("#answer").focus()

        $("#app").keydown(function(event) {
            console.log(event.keyCode)
            // event.ctrlKey = Ctr,  event.metaKey = Command(Mac)
            const shift = 16
            const backspace = 8
            const enter = 13
            if(event.ctrlKey || event.metaKey){
                if(event.keyCode === shift){
                    app.toggleVisible()
                }
                if(event.keyCode === enter){
                    console.log("わかった")
                    app.next()
                }
                else if(event.keyCode === backspace){
                    console.log("わからない")
                    app.markedUnknown()

                }

            }
        });
    }
})
// $(function() {
//     $("#answer").focus()
//     $("#answer").keydown(function(event) {
//         console.log(event.keyCode)
//         // event.ctrlKey = Ctr,  event.metaKey = Command(Mac)
//         const esc = 27
//         const backspace = 8
//         const enter = 13
//         if(event.ctrlKey || event.metaKey){
//             if(event.keyCode === enter){
//                 console.log("understand")
//             }
//             else if(event.keyCode === backspace){
//                 console.log("unknown")

//             }

//         }
//     });
// });
