import React from 'react';
import {shallow} from 'enzyme';
import renderer from 'react-test-renderer';

import NavBar from '../NavBar';

const title = 'Hello, World!';

test('NavBar.jsx renders properly', () => {
    const wrapper = shallow(<NavBar title={title}/>);
    const element = wrapper.find('strong');
    expect(element.length).toBe(1);
    expect(element.get(0).props.children).toBe(title);
});