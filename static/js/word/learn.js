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
        showMean: false,
        showOxfordMean: false,
        showSynonyms: false,
      },
    methods: {
        sound(e) {
            e.currentTarget.querySelector("audio").play()
        },
        toggleVisible(){
            this.meanShow = !this.meanShow
        },
        visibleMeaning(){
            this.meanShow = true;
            event.stopPropagation();
            return false;

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
        answerWord(is_unknown){
            const data = JSON.stringify({
                'word_log_id': this.wordLogId,
                'is_unknown': is_unknown
            });
            axios.post('/word/api/answer', data, this.ajaxConfig)
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
        this.showMean = params.dataset.showMean !== 'False';
        this.showOxfordMean = params.dataset.showOxfordMean !== 'False';
        this.showSynonyms = params.dataset.showSynonyms !== 'False';
        console.log(params.dataset.showMean)
        console.log(params.dataset.showOxfordMean)
        console.log(params.dataset.showSynonyms)

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
        window.scroll(0, 0);

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
                    app.answerWord(is_unknown=0)
                    event.stopPropagation();
                    return false;
                }
                // <-
                else if(event.keyCode === 37){
                    app.answerWord(is_unknown=1)
                    event.stopPropagation();
                    return false;

                }
                if(event.keyCode === 188){
                    app.showMean = !app.showMean
                    event.stopPropagation();
                    return false;
                }
                if(event.keyCode === 190){
                    app.showOxfordMean = !app.showOxfordMean
                    event.stopPropagation();
                    return false;
                }
                if(event.keyCode === 191){
                    app.showSynonyms = !app.showSynonyms
                    event.stopPropagation();
                    return false;
                }
            }
        });
    }
})