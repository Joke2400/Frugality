export { get, post, put, del}

interface RequestParams {
    method: string
    url: string;
    params?: {[key: string]: any}
}

async function request(requestParams: RequestParams): Promise<any> {
    let options: { [key: string]: any} = {
        method: requestParams.method,
    }
    if (requestParams.method === "GET") {
        options.headers = {
            "Accept": "text/html, application/json"
        }
        if (requestParams.params !== undefined) {
            requestParams.url += '?' + (
                new URLSearchParams(requestParams.params)).toString();
        }
    } else {
        options.body = JSON.stringify(requestParams);
        options.headers = {
            "Accept": "text/html, application/json",
            "Content-Type": "application/json"}
    }
    const response = await fetch(requestParams.url, options)
    if (!response.ok) {
        return Promise.reject(new Error("Unable to complete request."))
    }
    return await response.json()
}

const get = (
    url: string, params?: {[key: string]: any}) => request({method: "GET", url, params});
const post = (
    url: string, params?: {[key: string]: any}) => request({method: "POST", url, params});
const put = (
    url: string, params?: {[key: string]: any}) => request({method: "PUT", url, params});
const del = (
    url: string, params?: {[key: string]: any}) => request({method: "DEL", url, params});
