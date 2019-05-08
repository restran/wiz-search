/**
 * Created by restran on 2019/5/7.
 */
const options = {
    color: '#bffaf3',
    failedColor: '#874b4b',
    thickness: '5px',
    transition: {
        speed: '0.2s',
        opacity: '0.6s',
        termination: 300
    },
    autoRevert: true,
    location: 'left',
    inverse: false
};

Vue.use(VueProgressBar, options);
axios.defaults.headers.post['Content-Type'] = 'application/json; charset=utf-8';

var app = new Vue({
    el: '#app',
    data: function () {
        return {
            keyword: '',
            siteName: '为知搜',
            hasInit: false,
            hasSearch: false,
            total: 0,
            pageSize: 20,
            currentPage: 1,
            loading: false,
            tableData: []
        }
    },
    mounted: function () {
        this.hasInit = true
    },
    methods: {
        search: function () {
            this.loadPageList(1);
        },
        loadPageList: function (pageNum = 1) {
            var self = this;
            var postData = {
                'keyword': this.keyword,
                'page_num': pageNum
            };
            self.hasSearch = false;
            self.loading = true;
            // 这里加上随机数，避免缓存
            axios.post('/api/search?_t=' + Math.random(), postData)
                .then(function (response) {
                    if (typeof response.data === 'string') {
                        try {
                            response.data = JSON.parse(response.data)
                        } catch (e) {
                            console.log(e)
                        }
                    }

                    self.tableData = response.data['data'];
                    self.total = response.data['total'];
                    self.hasSearch = true;
                    self.loading = false;
                })
                .catch(function (error) {
                    self.showErrorMsg(error);
                    self.hasSearch = true;
                    self.loading = false;
                });
        },
        handleCurrentChange: function (val) {
            this.currentPage = val;
            console.log(`当前页: ${val}`);
            this.loadPageList(val);
        },
        showErrorMsg: function (e) {
            this.$message({
                message: e,
                type: 'warning',
                duration: 3000,
                showClose: true
            });
        }
    },
    watch: {}
});