angular.module('LabsterBackOffice')

  .controller('NewLicenseStep2Controller', function ($scope, $routeParams, $location, $http, localStorageService) {

    $scope.institution_vat_number = "";
    $scope.institution_name = window.requestUser.organization_name;
    $scope.tax = 0;
    $scope.subTotalPrice = 0;
    $scope.totalPrice = 0;
    $scope.vat_error = "";
    $scope.institution_error = "";
    $scope.institution_type = 1;
    $scope.institution = "";
    $scope.country = null;
    $scope.is_eu_country = false;
    $scope.is_denmark = false;
    $scope.isProcessing = false;
    $scope.loading_cc = false;
    $scope.loading_man = false;
    $scope.default_country = window.requestUser.backoffice.user.country;

    // get data from previous page
    var localStorage = localStorageService.get('paymentStorage');
    $scope.labs = localStorage.labs;
    $scope.subTotalPrice = localStorage.subTotalPrice;
    $scope.totalPrice = localStorage.totalPrice;

    // get list of country
    var url_country = window.backofficeUrls.country;
    $http.get(url_country)
      .success(function (data, status, headers, config) {
        $scope.countries = data.countries;
        $scope.countries_vat = data.countries_vat;
        $scope.country = $scope.countries[0];
        var idx_country = getIndexCountryByCode($scope.default_country, $scope.countries);
        if (idx_country != 0) {
          $scope.country = $scope.countries[idx_country];
        }
      });

    var duplicateLabs = function (list_product, payment_id, callback) {
      //callback();
      //return;

      var labs = [],
        post_data;
      angular.forEach(list_product, function (item) {
        angular.forEach(list_product.labster_labs, function (lab_id) {
          labs.push({
            lab_id: lab_id,
            license_count: item.item_count
          });
        });
      });

      var post_data = {labs: labs, payment_id: payment_id, token: window.requestUser.backoffice.token};
      var url = window.backofficeUrls.duplicateLabs;
      $http.post(url, post_data, {
        headers: {
          'Authorization': "Token " + window.requestUser.token
        }
      }).success(function (data, status, headers, config) {
        callback();
      }).error(function (data, status, headers, config) {
      });
    }; // end of duplicateLabs

    $scope.checkVat = function () {
      // call function checkVat() in vat.js
      var vatResult = checkVatHelper($scope.country, $scope.subTotalPrice, $scope.institution_type, $scope.countries_vat);

      $scope.totalPrice = vatResult.totalPrice;
      $scope.tax = vatResult.vat;
    };

    $scope.buyLabs = function (payment_method) {
      var list_product;

      $scope.isProcessing = true;
      if ($scope.institution_type != 1) {
        $scope.vat_error = checkVatFormat($scope.institution_vat_number);
        $scope.institution_error = checkInstitution($scope.institution_name);
      } else {
        $scope.vat_error = "";
        $scope.institution_error = "";
      }
      if (!$scope.institution_error.length && !$scope.vat_error.length) {
        // show loading spin
        if (payment_method == "manual") {
          $scope.loading_man = true;
        } else {
          $scope.loading_cc = true;
        }

        var url = window.backofficeUrls.buyLab;
        data = {
          user: window.requestUser.backoffice.user.id,
          is_teacher: true,
          payment_type: payment_method,
          institution_type : $scope.institution_type,
          institution_name : $scope.institution_name,
          country : $scope.country.id,
          total_before_tax : $scope.subTotalPrice,
          vat_number: $scope.institution_vat_number,
          list_product: []
        };

        angular.forEach($scope.labs, function (lab) {
          if (lab.license > 0) {
            if (lab.lab_type == "individual") {
              // include individual lab
              data.list_product.push({
                product: lab.id,
                labster_labs: [lab.external_id],
                item_count: lab.license,
                month_subscription: lab.month_subscription
              });
            } else {
              // include group package lab
              var item = {
                product_group: lab.id,
                labster_labs: [],
                item_count: lab.license,
                month_subscription: lab.month_subscription
              }
              angular.forEach(lab.products, function (each) {
                item.labster_labs.push(each.external_id);
              });
              data.list_product.push(item);
            }
          }
        });

        list_product = data.list_product;
        $http.post(url, data, {
          headers: {
            'Authorization': "Token " + window.requestUser.backoffice.token
          }
        })

          .success(function (data, status, headers, config) {
            duplicateLabs(list_product, data.id, function () {
              var url = '/invoice/' + data.id;
              $location.url(url);
            });
          })

          .error(function (data, status, headers, config) {
          });
      }
    };  // end of buy lab function
  });