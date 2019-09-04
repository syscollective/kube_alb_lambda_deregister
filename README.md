# kube_alb_lambda_deregister
Lambda function that gracefully deregisters instances from ALB prior to shutdown.

This function is part of a workaround for kubernetes' aws-alb-ingress-controller not deregistering instances from ALB in time when CA scales down, resulting in 502's to the clients in the period between instance shutdown and ALB halthchecks failure.

This is to be used with ALB + nodeport setup.

This will do 2 things:
1. Label nodes in Kubernetes with `alpha.service-controller.kubernetes.io/exclude-balancer: true`, so the aws-alb-ingress-controller will not add them back to the loadbalancer during shutdown.
2. Deregisters the instance from ALB to trigger 'draining' state and be removed gracefuly.

This should be triggered on lifecycle-hooks configured in the Autoscaler Group in AWS.
