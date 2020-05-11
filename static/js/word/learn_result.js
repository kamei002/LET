const app = new Vue({
    el: '#app',
    delimiters: ['${', '}'],
    data: {},
    methods: {
        toggleStar(e){
            console.log("toggleStar")
            const targetNode = e.currentTarget
            const data = targetNode.querySelector(".data").dataset
            const isChecked = data.isChecked === "True"
            const wordSummaryId = data.wordSummaryId
            let summaries = document.querySelectorAll(`.summary-${wordSummaryId}`)

            const submitData = JSON.stringify({
                'is_checked': !isChecked,
                'word_summary_id': wordSummaryId
            });
            axios.post('/word/api/star', submitData, this.ajaxConfig)
            .then(function(res){
                app.isChecked = res.data.is_checked

                let addClass = ""
                if(isChecked){
                    addClass = "fa-star-o"
                    dataIsCheck = "False"
                }
                else{
                    addClass = "fa-star"
                    dataIsCheck = "True"
                }
                console.log(typeof data)

                summaries.forEach(summary =>{
                    const icon = summary.querySelector("i");
                    const data = summary.querySelector(".data").dataset;
                    icon.classList.remove('fa-star-o');
                    icon.classList.remove('fa-star');
                    icon.classList.add(addClass);
                    data.isChecked = dataIsCheck;
                })
            })
            .catch(function(res){
                console.log(res)
            });

        },
    },
    created: function(){
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
})