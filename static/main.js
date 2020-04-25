(function () {

    'use strict';
  
    angular.module('WordcountApp', [])
  
    .controller('WordcountController', ['$scope', '$log', '$http', '$timeout',
    function($scope, $log, $http, $timeout) {

        $scope.submitButtonText = 'Submit';
        $scope.loading = false;
        $scope.urlerror = false;

        $scope.getResults = function() {

            // get the URL from the input
            let userInput = $scope.url;

            // fire the API request
            $http.post('/start', {"url": userInput}).
            success(function(jobId) {
                $log.log(jobId); 
                getWordCount(jobId);
                $scope.wordcounts = null;
                $scope.loading = true;
                $scope.submitButtonText = 'Loading...';
                $scope.urlerror = false;
            }).
            error(function(error) {
                $log.log(error);
            });
        };

        function getWordCount(jobID) {

            let timeout = "";
        
            let poller = function() {
            // check on job in queue
            $http.get('/results/'+jobID).
                success(function(data, status, headers, config) {

                    if(status === 202) {
                        $log.log(data, status);
                    } else if (status === 200){
                        $log.log(data);
                        $scope.loading = false;
                        $scope.submitButtonText = "Submit";
                        $scope.wordcounts = data;
                        $timeout.cancel(timeout);
                        return false;
                    }

                    // calls poller() every 2s until canceled
                    timeout = $timeout(poller, 2000);
                }).
                error(function(error) {
                  $log.log(error);
                  $scope.loading = false;
                  $scope.submitButtonText = "Submit";
                  $scope.urlerror = true;
                });
            };
            poller();
        }

    }])

    // for frequency chart & histogram
    .directive('wordCountChart', ['$parse', function ($parse) {
        return {
          restrict: 'E',
          replace: true,
          template: '<div id="chart"></div>',
          link: function (scope) {
            scope.$watch('wordcounts', function() {
                d3.select('#chart').selectAll('*').remove();
                let data = scope.wordcounts;
                for (let word in data) {
                    let key = data[word][0];
                    let value = data[word][1];
                    d3.select('#chart')
                        .append('div')
                        .selectAll('div')
                        .data(word)
                        .enter()
                        .append('div')
                        .style('width', function() {
                        return (value * 3) + 'px';
                        })
                        .text(function(d){
                        return key;
                        });
                }
              }, true);
          }
         };
      }]);
  
}());