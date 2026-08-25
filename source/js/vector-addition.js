(function() {

var board = JXG.JSXGraph.initBoard(
  boardElementId,
  {
    boundingbox:[-1,6,6,-1],
    axis:true
  }
);

var O = board.create('point',[0,0],
{
  visible:false,
  fixed:true
});

var U = board.create('point',[3,1],
{
  name:'u'
});

var V = board.create('point',[1,3],
{
  name:'v'
});

board.create('arrow',[O,U],
{
  strokeColor:'blue'
});

board.create('arrow',[O,V],
{
  strokeColor:'red'
});

var S = board.create('point',[
    function(){ return U.X()+V.X(); },
    function(){ return U.Y()+V.Y(); }
],
{
    visible:false
});

board.create('arrow',[O,S],
{
    strokeColor:'green',
    strokeWidth:4
});

})();