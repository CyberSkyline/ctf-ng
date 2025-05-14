import { useRoutes } from "react-router";

function TempRoute(){
    return <div>temp route</div>
}

function TempRoute2(){
    return <div>temp route 2</div>
}

function Routes(){
    const prefix = 'hello'
    const routes = useRoutes([
        {path: `/${prefix}`, element: <TempRoute/>},
        {path: `/${prefix}/temp`, element: <TempRoute2/>},
    ])
    
    return (
        <>{routes}</>
    )
}

export default Routes