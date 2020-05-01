const app = new Vue({
    el: '#app',
    delimiters: ['${', '}'],
    data: {
        errorAnswer: false,
        isChecked: false,
        meanShow: false,
        sending: false,
        visibleChecked: false,
        id: 0,
      },
    methods: {
        sound(e) {
            e.currentTarget.querySelector("audio").play()
        },
        toggleVisible(){
            this.meanShow = !this.meanShow
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
            if(app.sending === true){
                console.log("Now Sending...")
                return
            }
            app.sending=true
            if(this.hasErrorAnswer()){
                app.sending=false
                return
            }
            // location.reload();
            let url = `/word/learn?index=${app.index+1}`
            if(Number(app.categoryId)){
                url += `&category_id=${app.categoryId}`
            }
            if(Number(app.visibleChecked)){
                url += `&visible_checked=${app.visibleChecked}`
            }
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
        this.visibleChecked =  Number(params.dataset.visibleChecked);

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
                // _
                if(event.keyCode === 189){
                    app.toggleStar()
                    event.stopPropagation();
                    return false;
                }
                // ↓
                if(event.keyCode === 40){
                    document.querySelector("#audio").play()
                    event.stopPropagation();
                    return false;
                }
                // ↑
                if(event.keyCode === 38){
                    app.toggleVisible()
                    event.stopPropagation();
                    return false;
                }
                // ->
                if(event.keyCode === 39){
                    console.log("わかった")
                    app.next()
                    event.stopPropagation();
                    return false;
                }
                // <-
                else if(event.keyCode === 37){
                    console.log("わからない")
                    app.markedUnknown()
                    event.stopPropagation();
                    return false;

                }
            }
        });
    }
})