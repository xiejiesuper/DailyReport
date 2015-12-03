//<div>[title]</div>  字符串替换
;(function(window, document, undefined) {   
    function format(html,dict){
    var reg = new RegExp("\\[([^\\[\\]]*?)\\]", 'igm');
    var html = html.replace(reg, function (node, key) {
            return dict[key]||'';
        });
        return html    
    }
    Array.prototype.indexOf = function(val) {
        for (var i = 0; i < this.length; i++) {
        if (this[i] == val) return i;
        }
        return -1;
    };
    Array.prototype.remove = function(val) {
        var index = this.indexOf(val);
        if (index > -1) {
            this.splice(index, 1);
        }
    };
    
    window.format = format;   
    window.Array = Array;
 })(window, document);

